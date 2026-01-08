"""
Authentication service with database persistence.
Handles operator registration, login, and session management.
"""
from typing import Optional
from datetime import datetime, timedelta
from models import BaseModel
from pydantic import Field
from sqlalchemy.orm import Session
import bcrypt
import secrets

from db_models import OperatorDB, SessionDB


class Operator(BaseModel):
    id: str
    name: str
    role: str
    email: str
    department: str


class RegisterRequest(BaseModel):
    operator_id: str
    name: str
    email: str
    department: str
    role: str
    password: str


class LoginRequest(BaseModel):
    operator_id: str
    password: str
    role: Optional[str] = None


class LoginResponse(BaseModel):
    operator: Operator
    session_token: str
    expires_at: datetime


def register_operator(request: RegisterRequest, db: Session) -> Optional[Operator]:
    """
    Register a new operator in the database.
    """
    operator_id = request.operator_id.upper().strip()
    
    # Check if operator already exists
    existing = db.query(OperatorDB).filter(OperatorDB.id == operator_id).first()
    if existing:
        return None
    
    # Check if email already exists
    existing_email = db.query(OperatorDB).filter(OperatorDB.email == request.email).first()
    if existing_email:
        return None
    
    # Create new operator
    operator_db = OperatorDB(
        id=operator_id,
        name=request.name,
        email=request.email,
        department=request.department,
        role=request.role.lower(),
        password_hash=bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    )
    
    db.add(operator_db)
    db.commit()
    db.refresh(operator_db)
    
    return Operator(
        id=operator_db.id,
        name=operator_db.name,
        role=operator_db.role,
        email=operator_db.email,
        department=operator_db.department
    )


def authenticate_operator(operator_id: str, password: str, db: Session, role: Optional[str] = None) -> Optional[Operator]:
    """
    Authenticate an operator by ID and password.
    """
    operator_id = operator_id.upper().strip()
    
    # Query operator from database
    operator_db = db.query(OperatorDB).filter(OperatorDB.id == operator_id).first()
    if not operator_db:
        return None
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), operator_db.password_hash.encode('utf-8')):
        return None
    
    # If role is provided, verify it matches
    if role and operator_db.role != role:
        return None
    
    return Operator(
        id=operator_db.id,
        name=operator_db.name,
        role=operator_db.role,
        email=operator_db.email,
        department=operator_db.department
    )


def create_session(operator: Operator, db: Session) -> LoginResponse:
    """
    Create a new session for the authenticated operator.
    """
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Set expiration (24 hours from now)
    expires_at = datetime.now() + timedelta(hours=24)
    
    # Store session in database
    session_db = SessionDB(
        token=session_token,
        operator_id=operator.id,
        expires_at=expires_at
    )
    
    db.add(session_db)
    db.commit()
    
    return LoginResponse(
        operator=operator,
        session_token=session_token,
        expires_at=expires_at
    )


def verify_session(session_token: str, db: Session) -> Optional[Operator]:
    """
    Verify a session token and return the operator if valid.
    """
    # Query session from database
    session_db = db.query(SessionDB).filter(SessionDB.token == session_token).first()
    if not session_db:
        return None
    
    # Check if session has expired
    if datetime.now() > session_db.expires_at:
        db.delete(session_db)
        db.commit()
        return None
    
    # Get operator data
    operator_db = db.query(OperatorDB).filter(OperatorDB.id == session_db.operator_id).first()
    if not operator_db:
        return None
    
    return Operator(
        id=operator_db.id,
        name=operator_db.name,
        role=operator_db.role,
        email=operator_db.email,
        department=operator_db.department
    )


def logout(session_token: str, db: Session) -> bool:
    """
    Logout an operator by invalidating their session.
    """
    session_db = db.query(SessionDB).filter(SessionDB.token == session_token).first()
    if session_db:
        db.delete(session_db)
        db.commit()
        return True
    return False


def get_all_operators(db: Session) -> list[Operator]:
    """
    Get all registered operators (for admin purposes).
    """
    operators_db = db.query(OperatorDB).all()
    return [
        Operator(
            id=op.id,
            name=op.name,
            role=op.role,
            email=op.email,
            department=op.department
        )
        for op in operators_db
    ]
