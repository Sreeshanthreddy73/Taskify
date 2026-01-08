"""
Database initialization script with seed data.
Run this to create tables and populate initial data.
"""
from database import engine, Base, SessionLocal
from db_models import OperatorDB, DisruptionDB
from passlib.context import CryptContext
from datetime import datetime

# Password hashing - use bcrypt directly without deprecated parameter
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_operators(db):
    """Seed initial operator accounts"""
    operators = [
        {
            "id": "OP-001",
            "name": "Sarah Chen",
            "email": "sarah.chen@logitech.com",
            "role": "manager",
            "department": "Operations",
            "password": "manager123"
        },
        {
            "id": "OP-002",
            "name": "Marcus Rodriguez",
            "email": "marcus.rodriguez@logitech.com",
            "role": "operator",
            "department": "Logistics",
            "password": "operator123"
        },
        {
            "id": "OP-003",
            "name": "Aisha Patel",
            "email": "aisha.patel@logitech.com",
            "role": "analyst",
            "department": "Analytics",
            "password": "analyst123"
        },
        {
            "id": "OP-004",
            "name": "James Wilson",
            "email": "james.wilson@logitech.com",
            "role": "operator",
            "department": "Logistics",
            "password": "operator123"
        },
        {
            "id": "OP-005",
            "name": "Li Wei",
            "email": "li.wei@logitech.com",
            "role": "manager",
            "department": "Operations",
            "password": "manager123"
        }
    ]
    
    for op_data in operators:
        # Check if operator already exists
        existing = db.query(OperatorDB).filter(OperatorDB.id == op_data["id"]).first()
        if not existing:
            password = op_data.pop("password")
            operator = OperatorDB(
                **op_data,
                password_hash=hash_password(password)
            )
            db.add(operator)
    
    db.commit()
    print(f"✓ Seeded {len(operators)} operators")


def seed_disruptions(db):
    """Seed initial disruptions"""
    disruptions = [
        {
            "id": "DISR-001",
            "type": "port_strike",
            "location": "Chennai Port, India",
            "severity": "high",
            "description": "Labor strike affecting container operations at Chennai Port. Estimated 3-5 day delay for all shipments.",
            "status": "active"
        },
        {
            "id": "DISR-002",
            "type": "weather",
            "location": "Pacific Shipping Lane",
            "severity": "medium",
            "description": "Severe weather conditions in Pacific shipping routes causing delays. Typhoon warning issued.",
            "status": "active"
        },
        {
            "id": "DISR-003",
            "type": "route_closure",
            "location": "Suez Canal",
            "severity": "critical",
            "description": "Temporary closure due to vessel grounding. Major impact on Europe-Asia routes.",
            "status": "active"
        },
        {
            "id": "DISR-004",
            "type": "equipment_failure",
            "location": "Singapore Hub",
            "severity": "low",
            "description": "Crane malfunction at Singapore container terminal. Reduced processing capacity.",
            "status": "active"
        },
        {
            "id": "DISR-005",
            "type": "customs_delay",
            "location": "Rotterdam Port, Netherlands",
            "severity": "medium",
            "description": "Increased customs inspections causing processing delays. Average 2-day additional wait time.",
            "status": "active"
        }
    ]
    
    for disr_data in disruptions:
        # Check if disruption already exists
        existing = db.query(DisruptionDB).filter(DisruptionDB.id == disr_data["id"]).first()
        if not existing:
            disruption = DisruptionDB(**disr_data)
            db.add(disruption)
    
    db.commit()
    print(f"✓ Seeded {len(disruptions)} disruptions")


def init_database():
    """Initialize database with tables and seed data"""
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")
    
    # Seed data
    db = SessionLocal()
    try:
        seed_operators(db)
        seed_disruptions(db)
        print("[OK] Database initialization complete!")
    except Exception as e:
        print(f"[ERROR] Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
