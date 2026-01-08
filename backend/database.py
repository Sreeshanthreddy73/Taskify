"""
Database configuration and session management for LogiTech.
Uses SQLAlchemy with SQLite for persistent storage.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Database configuration
# Use /tmp for Vercel serverless (only writable directory)
DATABASE_DIR = os.environ.get("DATABASE_DIR", "/tmp")
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'logitech.db')}"

# Ensure data directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use with FastAPI's Depends() for automatic session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables and seeding data.
    Should be called on application startup.
    """
    from init_db import init_database
    init_database()
