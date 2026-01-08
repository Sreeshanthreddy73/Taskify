"""
Action ticket service with database persistence.
Manages action tickets for disruption responses.
"""
from typing import List, Optional
from datetime import datetime
from models import ActionTicket, Decision, ActionType
from services.data_service import get_shipment_by_id, get_route_by_id
from sqlalchemy.orm import Session
from db_models import ActionTicketDB


def create_action_ticket(
    disruption_id: str,
    decision: Decision,
    operator_id: str,
    db: Session
) -> ActionTicket:
    """
    Create an action ticket from a decision.
    Includes human-readable explanation.
    Prevents duplicates for same shipment-disruption pair.
    """
    # Check for existing ticket with same shipment_id and disruption_id
    existing_ticket = db.query(ActionTicketDB).filter(
        ActionTicketDB.shipment_id == decision.shipment_id,
        ActionTicketDB.disruption_id == disruption_id
    ).first()
    
    if existing_ticket:
        print(f"Ticket already exists for {decision.shipment_id} in {disruption_id}: {existing_ticket.id}")
        return ticket_db_to_model(existing_ticket)
    
    shipment = get_shipment_by_id(decision.shipment_id)
    
    # Generate ticket ID
    ticket_count = db.query(ActionTicketDB).count()
    ticket_id = f"TICKET-{(ticket_count + 1):03d}"
    
    # Generate detailed explanation
    explanation = generate_explanation(decision)
    
    # Create database record
    ticket_db = ActionTicketDB(
        id=ticket_id,
        disruption_id=disruption_id,
        shipment_id=decision.shipment_id,
        action_type=decision.action.value,
        explanation=explanation,
        destination=shipment.destination,
        estimated_delay=f"{decision.estimated_delay_hours} hours" if decision.estimated_delay_hours else None,
        priority=str(shipment.priority),
        created_by=operator_id,
        status="pending"
    )
    
    db.add(ticket_db)
    db.commit()
    db.refresh(ticket_db)
    
    return ticket_db_to_model(ticket_db)


def ticket_db_to_model(ticket_db: ActionTicketDB) -> ActionTicket:
    """Convert database model to Pydantic model"""
    return ActionTicket(
        id=ticket_db.id,
        disruption_id=ticket_db.disruption_id,
        shipment_id=ticket_db.shipment_id,
        destination=ticket_db.destination,
        action=ActionType(ticket_db.action_type),
        explanation=ticket_db.explanation,
        created_at=ticket_db.created_at,
        status=ticket_db.status,
        decision=None  # Decision object not stored in DB, only the result
    )


def generate_explanation(decision: Decision) -> str:
    """
    Generate a human-readable explanation for the decision.
    """
    shipment = get_shipment_by_id(decision.shipment_id)
    
    if decision.action == ActionType.REROUTE:
        alt_route = get_route_by_id(decision.alternative_route_id) if decision.alternative_route_id else None
        
        explanation = (
            f"**Decision: Reroute Shipment {shipment.id}**\n\n"
            f"We have decided to reroute this shipment because {decision.reasoning.lower()}.\n\n"
            f"**Shipment Details:**\n"
            f"- Priority: {shipment.priority}/10\n"
            f"- Cargo Type: {shipment.cargo_type.value.title()}\n"
            f"- Delay Tolerance: {shipment.delay_tolerance_hours} hours\n"
            f"- Cost Tolerance: {shipment.cost_increase_tolerance_percent}%\n\n"
        )
        
        if alt_route:
            explanation += (
                f"**Alternative Route:**\n"
                f"- Route: {alt_route.name}\n"
                f"- Estimated Duration: {alt_route.estimated_days} days\n"
                f"- Estimated Cost Impact: +{decision.estimated_cost_impact:.1f}%\n"
                f"- Additional Delay: {decision.estimated_delay_hours} hours\n\n"
            )
        
        explanation += (
            f"**Action Required:**\n"
            f"1. Coordinate with logistics team to redirect shipment\n"
            f"2. Update customer with new ETA\n"
            f"3. Arrange alternative route documentation\n"
            f"4. Monitor shipment progress on new route"
        )
    
    elif decision.action == ActionType.DELAY:
        explanation = (
            f"**Decision: Delay Shipment {shipment.id}**\n\n"
            f"We have decided to delay this shipment because {decision.reasoning.lower()}.\n\n"
            f"**Shipment Details:**\n"
            f"- Priority: {shipment.priority}/10\n"
            f"- Cargo Type: {shipment.cargo_type.value.title()}\n"
            f"- Delay Tolerance: {shipment.delay_tolerance_hours} hours\n"
            f"- Expected Delay: {decision.estimated_delay_hours} hours\n\n"
            f"**Rationale:**\n"
            f"The expected delay of {decision.estimated_delay_hours} hours is within the shipment's "
            f"tolerance of {shipment.delay_tolerance_hours} hours. This is the most cost-effective option "
            f"with minimal impact on delivery commitments.\n\n"
            f"**Action Required:**\n"
            f"1. Notify customer of expected delay\n"
            f"2. Update ETA in tracking system\n"
            f"3. Monitor disruption status for changes\n"
            f"4. Prepare contingency if delay extends"
        )
    
    else:  # ESCALATE
        explanation = (
            f"**Decision: Escalate Shipment {shipment.id}**\n\n"
            f"This shipment requires management review because {decision.reasoning.lower()}.\n\n"
            f"**Shipment Details:**\n"
            f"- Priority: {shipment.priority}/10\n"
            f"- Cargo Type: {shipment.cargo_type.value.title()}\n"
            f"- Delay Tolerance: {shipment.delay_tolerance_hours} hours\n"
            f"- Cost Tolerance: {shipment.cost_increase_tolerance_percent}%\n\n"
            f"**Why Escalation:**\n"
            f"This situation requires human judgment as it involves complex trade-offs between "
            f"cost, timing, and operational constraints that exceed automated decision parameters.\n\n"
            f"**Action Required:**\n"
            f"1. Escalate to logistics manager immediately\n"
            f"2. Prepare detailed impact analysis\n"
            f"3. Contact customer for priority clarification\n"
            f"4. Explore custom solutions with partners"
        )
    
    return explanation


def get_all_tickets(db: Session) -> List[ActionTicket]:
    """Get all action tickets from database"""
    tickets_db = db.query(ActionTicketDB).all()
    return [ticket_db_to_model(t) for t in tickets_db]


def get_ticket_by_id(ticket_id: str, db: Session) -> Optional[ActionTicket]:
    """Get a specific ticket by ID from database"""
    ticket_db = db.query(ActionTicketDB).filter(ActionTicketDB.id == ticket_id).first()
    if not ticket_db:
        return None
    return ticket_db_to_model(ticket_db)


def get_tickets_by_disruption(disruption_id: str, db: Session) -> List[ActionTicket]:
    """Get all tickets for a specific disruption from database"""
    tickets_db = db.query(ActionTicketDB).filter(ActionTicketDB.disruption_id == disruption_id).all()
    return [ticket_db_to_model(t) for t in tickets_db]


def update_ticket_status(ticket_id: str, status: str, db: Session) -> Optional[ActionTicket]:
    """Update ticket status in database"""
    ticket_db = db.query(ActionTicketDB).filter(ActionTicketDB.id == ticket_id).first()
    if not ticket_db:
        return None
    
    ticket_db.status = status
    db.commit()
    db.refresh(ticket_db)
    
    return ticket_db_to_model(ticket_db)


def add_ticket_note(ticket_id: str, note: str, db: Session) -> Optional[ActionTicket]:
    """Add a note to a ticket in database"""
    ticket_db = db.query(ActionTicketDB).filter(ActionTicketDB.id == ticket_id).first()
    if not ticket_db:
        return None
    
    # Append note to existing notes
    existing_notes = ticket_db.notes or ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_note = f"[{timestamp}] {note}"
    ticket_db.notes = f"{existing_notes}\n{new_note}" if existing_notes else new_note
    
    db.commit()
    db.refresh(ticket_db)
    
    return ticket_db_to_model(ticket_db)
