from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class DisruptionType(str, Enum):
    PORT_STRIKE = "port_strike"
    WEATHER = "weather"
    ROUTE_CLOSURE = "route_closure"
    EQUIPMENT_FAILURE = "equipment_failure"
    CUSTOMS_DELAY = "customs_delay"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CargoType(str, Enum):
    PERISHABLE = "perishable"
    STANDARD = "standard"
    BULK = "bulk"
    HAZARDOUS = "hazardous"


class ActionType(str, Enum):
    REROUTE = "reroute"
    DELAY = "delay"
    ESCALATE = "escalate"


class TicketStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Disruption(BaseModel):
    id: str
    type: DisruptionType
    location: str
    severity: Severity
    description: str
    timestamp: datetime
    estimated_duration_hours: Optional[int] = None
    affected_routes: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "DIS-001",
                "type": "port_strike",
                "location": "Chennai Port",
                "severity": "high",
                "description": "Labor strike affecting port operations",
                "timestamp": "2026-01-08T12:00:00",
                "estimated_duration_hours": 48,
                "affected_routes": ["ROUTE-001", "ROUTE-002"]
            }
        }


class Route(BaseModel):
    id: str
    name: str
    origin: str
    destination: str
    via_points: List[str] = []
    estimated_days: int
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ROUTE-001",
                "name": "Chennai to Singapore",
                "origin": "Chennai",
                "destination": "Singapore",
                "via_points": ["Colombo"],
                "estimated_days": 7,
                "is_active": True
            }
        }


class Shipment(BaseModel):
    id: str
    route_id: str
    cargo_type: CargoType
    priority: int = Field(ge=1, le=10, description="Priority level 1-10")
    delay_tolerance_hours: int = Field(ge=0, description="Maximum acceptable delay in hours")
    cost_increase_tolerance_percent: float = Field(ge=0, le=100, description="Max cost increase % allowed")
    current_status: str = "in_transit"
    destination: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SHIP-001",
                "route_id": "ROUTE-001",
                "cargo_type": "perishable",
                "priority": 9,
                "delay_tolerance_hours": 24,
                "cost_increase_tolerance_percent": 30.0,
                "current_status": "in_transit",
                "destination": "Singapore"
            }
        }


class ImpactAnalysis(BaseModel):
    disruption_id: str
    affected_routes: List[Route]
    affected_shipments: List[Shipment]
    total_shipments_impacted: int
    high_priority_count: int
    severity_score: float = Field(ge=0, le=10, description="Calculated impact severity")

    class Config:
        json_schema_extra = {
            "example": {
                "disruption_id": "DIS-001",
                "affected_routes": [],
                "affected_shipments": [],
                "total_shipments_impacted": 5,
                "high_priority_count": 2,
                "severity_score": 7.5
            }
        }


class Decision(BaseModel):
    shipment_id: str
    action: ActionType
    reasoning: str
    estimated_cost_impact: Optional[float] = None
    estimated_delay_hours: Optional[int] = None
    alternative_route_id: Optional[str] = None
    confidence_score: float = Field(ge=0, le=1, description="Decision confidence 0-1")

    class Config:
        json_schema_extra = {
            "example": {
                "shipment_id": "SHIP-001",
                "action": "reroute",
                "reasoning": "High priority shipment with low delay tolerance requires immediate rerouting",
                "estimated_cost_impact": 1500.0,
                "estimated_delay_hours": 12,
                "alternative_route_id": "ROUTE-003",
                "confidence_score": 0.95
            }
        }


class TicketNote(BaseModel):
    author: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ActionTicket(BaseModel):
    id: str
    disruption_id: str
    shipment_id: str
    destination: str
    action: ActionType
    decision: Decision
    explanation: str
    created_at: datetime
    status: TicketStatus = TicketStatus.PENDING
    assigned_to: Optional[str] = None
    notes: List[TicketNote] = []
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TICKET-001",
                "disruption_id": "DIS-001",
                "shipment_id": "SHIP-001",
                "destination": "Singapore",
                "action": "reroute",
                "decision": {},
                "explanation": "We rerouted this high-priority shipment because delay tolerance was only 24 hours",
                "created_at": "2026-01-08T12:30:00",
                "status": "pending",
                "notes": []
            }
        }


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "content": "This disruption affects 3 routes. Are high-priority shipments allowed to reroute with extra cost?",
                "timestamp": "2026-01-08T12:30:00"
            }
        }


class OperatorResponse(BaseModel):
    disruption_id: str
    allow_reroute: bool = True
    max_cost_increase_percent: float = Field(ge=0, le=100)
    prioritize_high_priority: bool = True
    additional_notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "disruption_id": "DIS-001",
                "allow_reroute": True,
                "max_cost_increase_percent": 25.0,
                "prioritize_high_priority": True,
                "additional_notes": "Focus on perishable goods first"
            }
        }
