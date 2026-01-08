"""
Disruption service with database persistence.
Manages supply chain disruptions.
"""
from typing import List, Optional
from models import Disruption
from sqlalchemy.orm import Session
from db_models import DisruptionDB


def get_all_disruptions(db: Session) -> List[Disruption]:
    """
    Get all active disruptions from database.
    """
    disruptions_db = db.query(DisruptionDB).filter(DisruptionDB.status == "active").all()
    return [
        Disruption(
            id=d.id,
            type=d.type,
            location=d.location,
            severity=d.severity,
            description=d.description,
            timestamp=d.created_at.isoformat() if d.created_at else None
        )
        for d in disruptions_db
    ]


def get_disruption(disruption_id: str, db: Session) -> Optional[Disruption]:
    """
    Get a specific disruption by ID from database.
    """
    disruption_db = db.query(DisruptionDB).filter(DisruptionDB.id == disruption_id).first()
    if not disruption_db:
        return None
    
    return Disruption(
        id=disruption_db.id,
        type=disruption_db.type,
        location=disruption_db.location,
        severity=disruption_db.severity,
        description=disruption_db.description,
        timestamp=disruption_db.created_at.isoformat() if disruption_db.created_at else None
    )


def create_disruption(disruption: Disruption, db: Session) -> Disruption:
    """
    Create a new disruption in the database.
    """
    disruption_db = DisruptionDB(
        id=disruption.id,
        type=disruption.type,
        location=disruption.location,
        severity=disruption.severity,
        description=disruption.description,
        status="active"
    )
    
    db.add(disruption_db)
    db.commit()
    db.refresh(disruption_db)
    
    return disruption


def update_disruption_status(disruption_id: str, status: str, db: Session) -> bool:
    """
    Update the status of a disruption.
    """
    disruption_db = db.query(DisruptionDB).filter(DisruptionDB.id == disruption_id).first()
    if not disruption_db:
        return False
    
    disruption_db.status = status
    db.commit()
    return True
