"""
Authentication dependency for FastAPI endpoints.
Validates operator ID from request headers.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from db_models import Operator


async def get_current_operator(
    x_operator_id: str = Header(..., description="Operator ID for authentication"),
    db: Session = Depends(get_db)
) -> Operator:
    """
    Validate operator ID from X-Operator-ID header.
    
    Args:
        x_operator_id: Operator ID from request header
        db: Database session
        
    Returns:
        Operator object if valid
        
    Raises:
        HTTPException: 401 if operator ID is invalid or missing
    """
    if not x_operator_id:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Operator-ID header"
        )
    
    operator = db.query(Operator).filter(
        Operator.operator_id == x_operator_id
    ).first()
    
    if not operator:
        raise HTTPException(
            status_code=401,
            detail="Invalid operator ID"
        )
    
    return operator
