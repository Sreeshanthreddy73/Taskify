"""
SQLAlchemy ORM models for LogiTech database.
These models represent the database schema.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


class OperatorDB(Base):
    """Database model for operators/users"""
    __tablename__ = "operators"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "OP-001"
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)  # manager, operator, analyst
    department = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DisruptionDB(Base):
    """Database model for supply chain disruptions"""
    __tablename__ = "disruptions"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "DISR-001"
    type = Column(String, nullable=False)  # port_strike, weather, route_closure, etc.
    location = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # critical, high, medium, low
    description = Column(Text, nullable=False)
    status = Column(String, default="active")  # active, resolved, monitoring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ActionTicketDB(Base):
    """Database model for action tickets"""
    __tablename__ = "action_tickets"
    
    id = Column(String, primary_key=True, index=True)  # e.g., "TKT-001"
    disruption_id = Column(String, ForeignKey("disruptions.id"), nullable=False, index=True)
    shipment_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)  # REROUTE, DELAY, ESCALATE
    status = Column(String, default="pending")  # pending, approved, in_progress, completed, rejected
    explanation = Column(Text, nullable=False)
    destination = Column(String, nullable=True)
    estimated_delay = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    
    # Tracking
    created_by = Column(String, ForeignKey("operators.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Notes
    notes = Column(Text, nullable=True)


class ConversationDB(Base):
    """Database model for AI conversation history"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    disruption_id = Column(String, ForeignKey("disruptions.id"), nullable=False, index=True)
    operator_id = Column(String, ForeignKey("operators.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SessionDB(Base):
    """Database model for active user sessions"""
    __tablename__ = "sessions"
    
    token = Column(String, primary_key=True, index=True)
    operator_id = Column(String, ForeignKey("operators.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
