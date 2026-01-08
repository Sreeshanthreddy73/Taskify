from typing import List, Dict
from models import Route, Shipment, CargoType

# In-memory storage for demo purposes
routes_db: Dict[str, Route] = {}
shipments_db: Dict[str, Shipment] = {}


def get_mock_routes() -> List[Route]:
    """Generate mock route data"""
    mock_routes = [
        Route(id="ROUTE-001", name="Chennai to Singapore", origin="Chennai", destination="Singapore", via_points=["Colombo"], estimated_days=7),
        Route(id="ROUTE-002", name="Chennai to Dubai", origin="Chennai", destination="Dubai", via_points=["Mumbai"], estimated_days=10),
        Route(id="ROUTE-003", name="Singapore to Los Angeles", origin="Singapore", destination="Los Angeles", via_points=["Tokyo"], estimated_days=18),
        Route(id="ROUTE-004", name="Rotterdam to Mumbai", origin="Rotterdam", destination="Mumbai", via_points=["Suez Canal", "Jeddah"], estimated_days=21),
        Route(id="ROUTE-005", name="Chennai to Hong Kong", origin="Chennai", destination="Hong Kong", via_points=["Singapore"], estimated_days=12),
        Route(id="ROUTE-006", name="Shanghai to San Francisco", origin="Shanghai", destination="San Francisco", via_points=[], estimated_days=16),
        Route(id="ROUTE-007", name="Hamburg to Singapore", origin="Hamburg", destination="Singapore", via_points=["Suez Canal", "Colombo"], estimated_days=24),
        Route(id="ROUTE-008", name="London to Chennai", origin="London", destination="Chennai", via_points=["Suez Canal"], estimated_days=20),
        Route(id="ROUTE-009", name="Rotterdam to New York", origin="Rotterdam", destination="New York", via_points=[], estimated_days=8),
        Route(id="ROUTE-010", name="Rotterdam to Shanghai", origin="Rotterdam", destination="Shanghai", via_points=["Suez Canal", "Singapore"], estimated_days=28),
    ]
    
    for route in mock_routes:
        routes_db[route.id] = route
    
    return mock_routes


def get_mock_shipments() -> List[Shipment]:
    """Generate mock shipment data"""
    mock_shipments = [
        Shipment(id="SHIP-001", route_id="ROUTE-001", cargo_type=CargoType.PERISHABLE, priority=9, delay_tolerance_hours=24, cost_increase_tolerance_percent=30.0, destination="Singapore"),
        Shipment(id="SHIP-002", route_id="ROUTE-001", cargo_type=CargoType.STANDARD, priority=5, delay_tolerance_hours=72, cost_increase_tolerance_percent=15.0, destination="Singapore"),
        Shipment(id="SHIP-003", route_id="ROUTE-002", cargo_type=CargoType.BULK, priority=3, delay_tolerance_hours=168, cost_increase_tolerance_percent=10.0, destination="Dubai"),
        Shipment(id="SHIP-004", route_id="ROUTE-003", cargo_type=CargoType.PERISHABLE, priority=10, delay_tolerance_hours=12, cost_increase_tolerance_percent=50.0, destination="Los Angeles"),
        Shipment(id="SHIP-005", route_id="ROUTE-004", cargo_type=CargoType.HAZARDOUS, priority=8, delay_tolerance_hours=48, cost_increase_tolerance_percent=20.0, destination="Mumbai"),
        Shipment(id="SHIP-006", route_id="ROUTE-005", cargo_type=CargoType.STANDARD, priority=6, delay_tolerance_hours=96, cost_increase_tolerance_percent=18.0, destination="Hong Kong"),
        Shipment(id="SHIP-007", route_id="ROUTE-003", cargo_type=CargoType.STANDARD, priority=4, delay_tolerance_hours=120, cost_increase_tolerance_percent=12.0, destination="Los Angeles"),
        Shipment(id="SHIP-008", route_id="ROUTE-004", cargo_type=CargoType.PERISHABLE, priority=9, delay_tolerance_hours=36, cost_increase_tolerance_percent=35.0, destination="Mumbai"),
        Shipment(id="SHIP-009", route_id="ROUTE-006", cargo_type=CargoType.BULK, priority=2, delay_tolerance_hours=240, cost_increase_tolerance_percent=8.0, destination="San Francisco"),
        Shipment(id="SHIP-010", route_id="ROUTE-007", cargo_type=CargoType.STANDARD, priority=7, delay_tolerance_hours=60, cost_increase_tolerance_percent=22.0, destination="Singapore"),
    ]
    
    for shipment in mock_shipments:
        shipments_db[shipment.id] = shipment
    
    return mock_shipments


def get_all_routes() -> List[Route]:
    """Get all routes"""
    if not routes_db:
        get_mock_routes()
    return list(routes_db.values())


def get_all_shipments() -> List[Shipment]:
    """Get all shipments"""
    if not shipments_db:
        get_mock_shipments()
    return list(shipments_db.values())


def get_route_by_id(route_id: str) -> Route:
    """Get a specific route by ID"""
    if not routes_db:
        get_mock_routes()
    
    if route_id not in routes_db:
        raise ValueError(f"Route {route_id} not found")
    
    return routes_db[route_id]


def get_shipment_by_id(shipment_id: str) -> Shipment:
    """Get a specific shipment by ID"""
    if not shipments_db:
        get_mock_shipments()
    
    if shipment_id not in shipments_db:
        raise ValueError(f"Shipment {shipment_id} not found")
    
    return shipments_db[shipment_id]


def get_shipments_by_route(route_id: str) -> List[Shipment]:
    """Get all shipments on a specific route"""
    if not shipments_db:
        get_mock_shipments()
    
    return [s for s in shipments_db.values() if s.route_id == route_id]
