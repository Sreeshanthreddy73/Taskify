from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models import (
    Disruption, ImpactAnalysis, Decision, ActionTicket,
    OperatorResponse, ConversationMessage, Severity
)
from services import disruption_service, impact_service, decision_engine, action_service, ai_service, auth_service
from database import get_db, init_db

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Disruption Response System",
    description="AI-assisted, agent-driven disruption response system for LogiTech",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register(request: auth_service.RegisterRequest, db: Session = Depends(get_db)):
    """Register a new operator"""
    try:
        operator = auth_service.register_operator(request, db)
        if not operator:
            raise HTTPException(
                status_code=400,
                detail="Operator ID or email already exists"
            )
        return {"message": "Operator registered successfully", "operator": operator}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login")
async def login(request: auth_service.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an operator and create a session"""
    try:
        # Authenticate operator
        operator = auth_service.authenticate_operator(
            operator_id=request.operator_id,
            password=request.password,
            db=db,
            role=request.role
        )
        
        if not operator:
            raise HTTPException(
                status_code=401,
                detail="Invalid operator ID or password"
            )
        
        # Create session
        login_response = auth_service.create_session(operator, db)
        
        return login_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Logout an operator by invalidating their session"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No session token provided")
        
        session_token = authorization.replace("Bearer ", "")
        success = auth_service.logout(session_token, db)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Logged out successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/verify")
async def verify_session(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Verify a session token and return operator info"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No session token provided")
        
        session_token = authorization.replace("Bearer ", "")
        operator = auth_service.verify_session(session_token, db)
        
        if not operator:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        return {"operator": operator}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/operators")
async def get_operators(db: Session = Depends(get_db)):
    """Get all registered operators (for demo purposes)"""
    try:
        return auth_service.get_all_operators(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DISRUPTION ENDPOINTS
# ============================================================================



@app.get("/api/disruptions", response_model=List[Disruption])
async def get_disruptions(db: Session = Depends(get_db)):
    """Get all active disruptions"""
    try:
        return disruption_service.get_all_disruptions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/disruptions/{disruption_id}", response_model=Disruption)
async def get_disruption(disruption_id: str, db: Session = Depends(get_db)):
    """Get a specific disruption by ID"""
    try:
        disruption = disruption_service.get_disruption(disruption_id, db)
        if not disruption:
            raise HTTPException(status_code=404, detail=f"Disruption {disruption_id} not found")
        return disruption
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/disruptions/severity/{severity}", response_model=List[Disruption])
async def get_disruptions_by_severity(severity: Severity):
    """Filter disruptions by severity level"""
    try:
        return disruption_service.get_disruptions_by_severity(severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# IMPACT ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/api/impact/{disruption_id}", response_model=ImpactAnalysis)
async def analyze_impact(disruption_id: str):
    """Analyze the impact of a disruption"""
    try:
        return impact_service.analyze_disruption_impact(disruption_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI CONVERSATION ENDPOINTS
# ============================================================================

@app.get("/api/conversation/question/{disruption_id}")
async def get_initial_question(disruption_id: str):
    """Get the initial AI-generated question for a disruption"""
    try:
        impact = impact_service.analyze_disruption_impact(disruption_id)
        question = ai_service.generate_initial_question(impact)
        
        message = ai_service.create_conversation_message(
            role="assistant",
            content=question
        )
        
        return {
            "message": message,
            "impact": impact
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversation/parse")
async def parse_operator_message(message: dict):
    """Parse operator's natural language response"""
    try:
        user_message = message.get("content", "")
        parsed = ai_service.parse_operator_input(user_message)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DECISION ENGINE ENDPOINTS
# ============================================================================

@app.post("/api/decisions/{disruption_id}", response_model=List[Decision])
async def make_decisions(disruption_id: str, operator_response: OperatorResponse):
    """
    Process decisions for all affected shipments based on operator input.
    This uses the deterministic decision engine (no AI).
    """
    try:
        # Get impact analysis
        impact = impact_service.analyze_disruption_impact(disruption_id)
        
        # Get disruption details for duration
        disruption = disruption_service.get_disruption_by_id(disruption_id)
        
        # Process decisions
        decisions = decision_engine.process_disruption_decisions(
            disruption_id=disruption_id,
            affected_shipments=impact.affected_shipments,
            operator_response=operator_response,
            disruption_duration_hours=disruption.estimated_duration_hours
        )
        
        return decisions
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ACTION TICKET ENDPOINTS
# ============================================================================

@app.post("/api/tickets/{disruption_id}", response_model=List[ActionTicket])
async def create_tickets(disruption_id: str, operator_response: OperatorResponse, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """
    Create action tickets for all affected shipments.
    This is the complete end-to-end flow.
    """
    try:
        # Get operator ID from session
        operator_id = "unknown"
        if authorization and authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
            operator = auth_service.verify_session(session_token, db)
            if operator:
                operator_id = operator.id
        
        # Get impact analysis
        # Get disruption details
        disruption = disruption_service.get_disruption(disruption_id, db)
        if not disruption:
            raise HTTPException(status_code=404, detail="Disruption not found")
        
        # Get impact analysis with db session
        impact = impact_service.analyze_disruption_impact(disruption_id, db)
        print(f"Impact Analysis: {len(impact.affected_shipments)} shipments affected")
        
        # Process decisions
        decisions = decision_engine.process_disruption_decisions(
            disruption_id=disruption_id,
            affected_shipments=impact.affected_shipments,
            operator_response=operator_response,
            disruption_duration_hours=disruption.estimated_duration_hours if disruption.estimated_duration_hours else 72 # Use actual duration or default
        )
        print(f"Decision Engine: Generated {len(decisions)} decisions")
        
        # Create tickets in database
        created_tickets = []
        for decision in decisions:
            ticket = action_service.create_action_ticket(
                disruption_id=disruption_id,
                decision=decision,
                operator_id=operator_id,
                db=db
            )
            if ticket:
                created_tickets.append(ticket)
        
        print(f"Created {len(created_tickets)} tickets for disruption {disruption_id}")
        return created_tickets
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error creating tickets: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets", response_model=List[ActionTicket])
async def get_all_tickets(db: Session = Depends(get_db)):
    """Get all action tickets"""
    try:
        return action_service.get_all_tickets(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets/{ticket_id}", response_model=ActionTicket)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get a specific ticket by ID"""
    try:
        ticket = action_service.get_ticket_by_id(ticket_id, db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets/disruption/{disruption_id}", response_model=List[ActionTicket])
async def get_tickets_by_disruption(disruption_id: str, db: Session = Depends(get_db)):
    """Get all tickets for a specific disruption"""
    try:
        return action_service.get_tickets_by_disruption(disruption_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/tickets/{ticket_id}/status")
async def update_ticket(ticket_id: str, update: dict, db: Session = Depends(get_db)):
    """Update ticket status (generic)"""
    try:
        status = update.get("status")
        ticket = action_service.update_ticket_status(ticket_id, status, db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/approve")
async def approve_ticket(ticket_id: str, request: dict, db: Session = Depends(get_db)):
    """Approve a ticket"""
    try:
        ticket = action_service.update_ticket_status(ticket_id, "approved", db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/reject")
async def reject_ticket(ticket_id: str, request: dict, db: Session = Depends(get_db)):
    """Reject a ticket"""
    try:
        ticket = action_service.update_ticket_status(ticket_id, "rejected", db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/start")
async def start_ticket(ticket_id: str, request: dict, db: Session = Depends(get_db)):
    """Start working on a ticket"""
    try:
        ticket = action_service.update_ticket_status(ticket_id, "in_progress", db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/complete")
async def complete_ticket(ticket_id: str, request: dict, db: Session = Depends(get_db)):
    """Complete a ticket"""
    try:
        ticket = action_service.update_ticket_status(ticket_id, "completed", db)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/approve")
async def approve_ticket(ticket_id: str, data: dict):
    """Approve a ticket"""
    try:
        operator_id = data.get("operator_id", "unknown")
        return action_service.approve_ticket(ticket_id, operator_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/reject")
async def reject_ticket(ticket_id: str, data: dict):
    """Reject a ticket"""
    try:
        operator_id = data.get("operator_id", "unknown")
        reason = data.get("reason", "No reason provided")
        return action_service.reject_ticket(ticket_id, operator_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/start")
async def start_ticket(ticket_id: str, data: dict):
    """Start working on a ticket"""
    try:
        operator_id = data.get("operator_id", "unknown")
        return action_service.start_ticket(ticket_id, operator_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/complete")
async def complete_ticket(ticket_id: str, data: dict):
    """Complete a ticket"""
    try:
        operator_id = data.get("operator_id", "unknown")
        notes = data.get("notes")
        return action_service.complete_ticket(ticket_id, operator_id, notes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/{ticket_id}/notes")
async def add_ticket_note(ticket_id: str, data: dict, db: Session = Depends(get_db)):
    """Add a note to a ticket"""
    try:
        content = data.get("content", "")
        note = f"{content}"
        ticket = action_service.add_ticket_note(ticket_id, note, db)
        
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUMMARY ENDPOINT (Complete Flow)
# ============================================================================

@app.post("/api/summary/{disruption_id}")
async def get_decision_summary(disruption_id: str, operator_response: OperatorResponse, db: Session = Depends(get_db)):
    """Get AI-generated summary of all decisions"""
    try:
        # Get disruption details
        disruption = disruption_service.get_disruption(disruption_id, db)
        if not disruption:
            raise HTTPException(status_code=404, detail="Disruption not found")
        
        # Get impact analysis
        impact = impact_service.analyze_disruption_impact(disruption_id, db)
        
        # Process decisions
        decisions = decision_engine.process_disruption_decisions(
            disruption_id=disruption_id,
            affected_shipments=impact.affected_shipments,
            operator_response=operator_response,
            disruption_duration_hours=72  # Default duration
        )
        
        # Generate summary
        summary = ai_service.generate_decision_summary(decisions, operator_response)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Serve Frontend Static Files (Catch-all)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
print(f"DEBUG: Frontend Directory resolved to: {frontend_dir}")
print(f"DEBUG: Directory exists? {os.path.exists(frontend_dir)}")

# Explicit root route for index.html (ALWAYS REGISTERED)
@app.get("/")
async def read_root():
    if not os.path.exists(frontend_dir):
         print("ERROR: Frontend directory not found!")
         raise HTTPException(status_code=500, detail="Frontend directory not found")
    return FileResponse(os.path.join(frontend_dir, "index.html"))

if os.path.exists(frontend_dir):
    # Mount /static for explicit asset loading if needed
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    # Mount root to serve other files (css, js) - MUST BE LAST
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
