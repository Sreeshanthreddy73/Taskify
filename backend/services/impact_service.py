from typing import List
from models import Disruption, ImpactAnalysis, Route, Shipment, Severity
from services.disruption_service import get_disruption
from services.data_service import get_all_routes, get_all_shipments, get_route_by_id


def analyze_disruption_impact(disruption_id: str, db=None) -> ImpactAnalysis:
    """
    Analyze the impact of a disruption on routes and shipments.
    
    This is a deterministic analysis based on:
    - Which routes are affected by the disruption
    - Which shipments are on those routes
    - Priority levels of affected shipments
    """
    from database import SessionLocal
    
    # Get database session if not provided
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        disruption = get_disruption(disruption_id, db)
        if not disruption:
            raise ValueError(f"Disruption {disruption_id} not found")
        
        all_routes = get_all_routes()
        all_shipments = get_all_shipments()
        
        # Find affected routes (using mock data since routes aren't in DB yet)
        affected_routes: List[Route] = []
        # Note: disruption from DB doesn't have affected_routes field
        # For now, we'll use mock logic based on location
        # Check if route locations are mentioned in disruption location
        # e.g. "Chennai" in "Chennai Port, India"
        for route in all_routes:
            # Check if matching via points
            via_match = any(point in disruption.location for point in route.via_points)
            
            # Simple keyword matching for ocean regions if not explicit
            if "Pacific" in disruption.location and "Pacific Ocean" in route.via_points:
                via_match = True
                
            if (route.origin in disruption.location or 
                route.destination in disruption.location or 
                disruption.location in route.name or
                via_match):
                affected_routes.append(route)
        
        # Find affected shipments (shipments on affected routes)
        affected_shipments: List[Shipment] = []
        high_priority_count = 0
        
        affected_route_ids = [r.id for r in affected_routes]
        for shipment in all_shipments:
            if shipment.route_id in affected_route_ids:
                affected_shipments.append(shipment)
                if shipment.priority >= 8:  # High priority threshold
                    high_priority_count += 1
        
        # Calculate severity score (0-10 scale)
        severity_score = calculate_severity_score(
            disruption=disruption,
            affected_shipments=affected_shipments,
            high_priority_count=high_priority_count
        )
        
        return ImpactAnalysis(
            disruption_id=disruption_id,
            affected_routes=affected_routes,
            affected_shipments=affected_shipments,
            total_shipments_impacted=len(affected_shipments),
            high_priority_count=high_priority_count,
            severity_score=severity_score
        )
    finally:
        if should_close:
            db.close()


def calculate_severity_score(
    disruption: Disruption,
    affected_shipments: List[Shipment],
    high_priority_count: int
) -> float:
    """
    Calculate a severity score based on multiple factors.
    
    Factors:
    - Disruption severity (base score)
    - Number of affected shipments
    - Number of high-priority shipments
    """
    # Base score from disruption severity
    severity_map = {
        "low": 2.0,
        "medium": 5.0,
        "high": 7.5,
        "critical": 9.0
    }
    base_score = severity_map.get(disruption.severity.lower() if hasattr(disruption.severity, 'lower') else str(disruption.severity).lower(), 5.0)
    
    # Impact multiplier based on affected shipments
    shipment_multiplier = 1.0
    if len(affected_shipments) > 10:
        shipment_multiplier = 1.5
    elif len(affected_shipments) > 5:
        shipment_multiplier = 1.3
    
    # High priority multiplier
    priority_multiplier = 1.0
    if high_priority_count > 0:
        priority_multiplier = 1.0 + (high_priority_count * 0.1)
    
    # Calculate final score (capped at 10.0)
    final_score = base_score * shipment_multiplier * priority_multiplier
    return min(final_score, 10.0)


def get_alternative_routes(origin: str, destination: str, exclude_route_ids: List[str]) -> List[Route]:
    """
    Find alternative routes between origin and destination.
    Excludes routes that are affected by disruptions.
    """
    all_routes = get_all_routes()
    alternatives = []
    
    for route in all_routes:
        if (route.origin == origin and 
            route.destination == destination and 
            route.id not in exclude_route_ids and
            route.is_active):
            alternatives.append(route)
    
    return alternatives
