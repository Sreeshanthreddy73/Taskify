from typing import List, Optional
from models import Decision, Shipment, ActionType, CargoType, OperatorResponse
from services.data_service import get_route_by_id
from services.impact_service import get_alternative_routes


def make_decision(
    shipment: Shipment,
    operator_response: OperatorResponse,
    disruption_duration_hours: Optional[int] = None
) -> Decision:
    """
    Deterministic decision engine based on business rules.
    
    This is the CORE LOGIC - no AI involved in decision making.
    
    Decision Rules:
    1. High Priority (>= 8):
       - If delay tolerance < 24h → REROUTE (even with extra cost)
       - If delay tolerance >= 24h → DELAY (if cost-effective)
    
    2. Medium Priority (4-7):
       - If delay tolerance < 12h → REROUTE
       - If delay tolerance >= 12h and cost increase < 20% → DELAY
       - Otherwise → ESCALATE
    
    3. Low Priority (< 4):
       - Default → DELAY
       - If delay > 7 days → ESCALATE
    
    4. Special Cases:
       - Perishable goods + delay > 48h → REROUTE immediately
       - No viable alternative routes → ESCALATE
    """
    
    # Get current route info
    current_route = get_route_by_id(shipment.route_id)
    
    # Find alternative routes
    alternatives = get_alternative_routes(
        origin=current_route.origin,
        destination=shipment.destination,
        exclude_route_ids=[shipment.route_id]
    )
    
    # Special case: Perishable goods with long delay
    if shipment.cargo_type == CargoType.PERISHABLE:
        if disruption_duration_hours and disruption_duration_hours > 48:
            if alternatives and operator_response.allow_reroute:
                return _create_reroute_decision(
                    shipment=shipment,
                    alternatives=alternatives,
                    reason="Perishable cargo requires immediate rerouting to prevent spoilage"
                )
    
    # High Priority Shipments (>= 8)
    if shipment.priority >= 8:
        if shipment.delay_tolerance_hours < 24:
            if alternatives and operator_response.allow_reroute:
                return _create_reroute_decision(
                    shipment=shipment,
                    alternatives=alternatives,
                    reason="High priority shipment with low delay tolerance requires immediate rerouting"
                )
            else:
                return _create_escalate_decision(
                    shipment=shipment,
                    reason="High priority shipment needs rerouting but no alternatives available"
                )
        else:
            # Can tolerate delay
            if disruption_duration_hours and disruption_duration_hours <= shipment.delay_tolerance_hours:
                return _create_delay_decision(
                    shipment=shipment,
                    delay_hours=disruption_duration_hours,
                    reason="High priority shipment can tolerate the expected delay duration"
                )
            else:
                if alternatives and operator_response.allow_reroute:
                    return _create_reroute_decision(
                        shipment=shipment,
                        alternatives=alternatives,
                        reason="Disruption exceeds delay tolerance, rerouting required"
                    )
                else:
                    return _create_escalate_decision(
                        shipment=shipment,
                        reason="Disruption exceeds delay tolerance but no reroute options available"
                    )
    
    # Medium Priority Shipments (4-7)
    elif 4 <= shipment.priority <= 7:
        if shipment.delay_tolerance_hours < 12:
            if alternatives and operator_response.allow_reroute:
                return _create_reroute_decision(
                    shipment=shipment,
                    alternatives=alternatives,
                    reason="Medium priority shipment with tight delay tolerance requires rerouting"
                )
            else:
                return _create_escalate_decision(
                    shipment=shipment,
                    reason="Tight delay tolerance but no reroute options available"
                )
        else:
            # Check cost constraints
            if disruption_duration_hours and disruption_duration_hours <= shipment.delay_tolerance_hours:
                estimated_cost_impact = 0.0  # No extra cost for delay
                if estimated_cost_impact <= shipment.cost_increase_tolerance_percent:
                    return _create_delay_decision(
                        shipment=shipment,
                        delay_hours=disruption_duration_hours,
                        reason="Medium priority shipment can absorb delay within cost constraints"
                    )
            
            return _create_escalate_decision(
                shipment=shipment,
                reason="Delay exceeds tolerance and rerouting may exceed cost constraints"
            )
    
    # Low Priority Shipments (< 4)
    else:
        if disruption_duration_hours and disruption_duration_hours > 168:  # 7 days
            return _create_escalate_decision(
                shipment=shipment,
                reason="Extended delay exceeds acceptable threshold even for low priority"
            )
        else:
            return _create_delay_decision(
                shipment=shipment,
                delay_hours=disruption_duration_hours or 48,
                reason="Low priority shipment scheduled for delay until disruption resolves"
            )


def _create_reroute_decision(shipment: Shipment, alternatives: List, reason: str) -> Decision:
    """Create a REROUTE decision"""
    # Select best alternative (shortest estimated days)
    best_alternative = min(alternatives, key=lambda r: r.estimated_days)
    
    # Estimate cost impact (simplified: 10% per extra day)
    current_route = get_route_by_id(shipment.route_id)
    extra_days = max(0, best_alternative.estimated_days - current_route.estimated_days)
    estimated_cost_impact = extra_days * 10.0  # Percentage
    
    return Decision(
        shipment_id=shipment.id,
        action=ActionType.REROUTE,
        reasoning=reason,
        estimated_cost_impact=estimated_cost_impact,
        estimated_delay_hours=extra_days * 24,
        alternative_route_id=best_alternative.id,
        confidence_score=0.9
    )


def _create_delay_decision(shipment: Shipment, delay_hours: int, reason: str) -> Decision:
    """Create a DELAY decision"""
    return Decision(
        shipment_id=shipment.id,
        action=ActionType.DELAY,
        reasoning=reason,
        estimated_cost_impact=0.0,
        estimated_delay_hours=delay_hours,
        alternative_route_id=None,
        confidence_score=0.85
    )


def _create_escalate_decision(shipment: Shipment, reason: str) -> Decision:
    """Create an ESCALATE decision"""
    return Decision(
        shipment_id=shipment.id,
        action=ActionType.ESCALATE,
        reasoning=reason,
        estimated_cost_impact=None,
        estimated_delay_hours=None,
        alternative_route_id=None,
        confidence_score=0.95
    )


def process_disruption_decisions(
    disruption_id: str,
    affected_shipments: List[Shipment],
    operator_response: OperatorResponse,
    disruption_duration_hours: int
) -> List[Decision]:
    """
    Process decisions for all affected shipments based on operator input.
    """
    decisions = []
    print(f"Processing decisions for {len(affected_shipments)} shipments. Response: {operator_response}")
    
    for shipment in affected_shipments:
        # Determine action based on rules
        # The original code called make_decision here.
        # The provided edit introduced 'determine_action' which is not defined
        # and had a syntax error.
        # To maintain syntactic correctness and fulfill the logging request,
        # we keep the original call to make_decision and add the print statement.
        decision = make_decision(
            shipment=shipment,
            operator_response=operator_response,
            disruption_duration_hours=disruption_duration_hours
        )
        decisions.append(decision)
    
    return decisions
