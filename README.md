# LogiTech - AI-Assisted Supply Chain Disruption Response System

## 🎯 Problem Statement

**Supply chains frequently fail not because disruptions are unknown, but because responses are slow, uncoordinated, or inconsistent.**

Current systems raise alerts but do not help operators decide what to do next. When disruptions occur (port strikes, severe weather, route closures), logistics teams waste critical time:
- Manually analyzing impact across routes and shipments
- Debating response options without clear decision frameworks
- Coordinating actions across disconnected systems
- Explaining decisions after the fact

This delay costs millions in missed deliveries, spoiled goods, and customer dissatisfaction.

## 💡 Solution

**LogiTech** is an AI-assisted, agent-driven disruption response system that converts disruption signals into validated logistics actions.

### How It Works

1. **Disruption Detected** → System identifies or receives disruption events
2. **AI Engages** → Conversational interface asks clarifying questions about priorities and constraints
3. **Backend Decides** → Deterministic rule engine evaluates impact and generates decisions
4. **Actions Created** → System generates action tickets with clear explanations
5. **AI Explains** → Natural language summaries explain why each decision was made

### Key Features

- 🚨 **Real-time Disruption Feed** - Monitor active disruptions with severity levels
- 💬 **AI-Assisted Conversation** - Natural language interface guides decision-making
- 🎯 **Deterministic Decision Engine** - Rule-based logic ensures consistent, auditable decisions
- 📋 **Action Tickets** - Clear, actionable recommendations with detailed explanations
- 🌍 **Global Scope** - Designed for worldwide supply chain operations

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Disruption    │──────▶│  Impact Analysis │──────▶│  AI Assistant   │
│     Service     │      │     Service      │      │   (Questions)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                             │
                                                             ▼
                                                    ┌─────────────────┐
                                                    │    Operator     │
                                                    │    Response     │
                                                    └─────────────────┘
                                                             │
                                                             ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Action Ticket  │◀─────│ Decision Engine  │◀─────│  AI Assistant   │
│    Service      │      │  (Rule-Based)    │      │  (Explanation)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11
- FastAPI (modern, fast web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Frontend:**
- Vanilla HTML5, CSS3, JavaScript (ES6+)
- Modern CSS (Grid, Flexbox, Custom Properties)
- Fetch API for backend communication

**Deployment:**
- Docker & Docker Compose
- Nginx (frontend static file serving)
- Containerized microservices

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- Docker Compose installed
- Git (for cloning)

### Installation & Running

```bash
# Clone the repository
git clone <repository-url>
cd LogiTech

# Start all services with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000/docs
```

That's it! The entire system will be running with one command.

### Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📖 Usage Guide

### 1. View Active Disruptions

- The left panel shows all active disruptions
- Filter by severity: Critical, High, Medium, Low
- Each card shows location, type, duration, and affected routes

### 2. Analyze a Disruption

- Click on any disruption card
- The AI assistant will analyze impact and ask clarifying questions
- Questions cover: rerouting permissions, cost tolerance, priority preferences

### 3. Provide Guidance

- Type your response in natural language
- Examples:
  - "Yes, reroute high-priority shipments with up to 30% cost increase"
  - "Delay all shipments, no rerouting"
  - "Prioritize perishable goods, max 25% cost increase"

### 4. Review Action Tickets

- The right panel displays generated action tickets
- Each ticket includes:
  - Action type (Reroute, Delay, Escalate)
  - Detailed explanation
  - Estimated impact
  - Required next steps

## 🧠 Decision Engine Rules

The system uses **deterministic, rule-based logic** (not AI) for decision-making:

### High Priority Shipments (Priority ≥ 8)
- Delay tolerance < 24h → **REROUTE** (even with extra cost)
- Delay tolerance ≥ 24h → **DELAY** (if within tolerance)

### Medium Priority Shipments (Priority 4-7)
- Delay tolerance < 12h → **REROUTE**
- Delay tolerance ≥ 12h and cost increase < 20% → **DELAY**
- Otherwise → **ESCALATE**

### Low Priority Shipments (Priority < 4)
- Default → **DELAY**
- Delay > 7 days → **ESCALATE**

### Special Cases
- Perishable goods + delay > 48h → **REROUTE immediately**
- No viable alternative routes → **ESCALATE**

## 📡 API Documentation

### Disruptions

```http
GET /api/disruptions
GET /api/disruptions/{disruption_id}
GET /api/disruptions/severity/{severity}
```

### Impact Analysis

```http
GET /api/impact/{disruption_id}
```

### Conversation

```http
GET /api/conversation/question/{disruption_id}
POST /api/conversation/parse
```

### Decisions & Tickets

```http
POST /api/decisions/{disruption_id}
POST /api/tickets/{disruption_id}
GET /api/tickets
GET /api/tickets/{ticket_id}
PATCH /api/tickets/{ticket_id}/status
```

### Summary

```http
POST /api/summary/{disruption_id}
```

Full interactive API documentation available at: `http://localhost:8000/docs`

## 🎓 Domain Alignment: LogiTech

This project addresses a critical **LogiTech (Logistics & Supply Chain)** problem:

- **Problem Domain**: Operational efficiency and visibility during disruptions
- **Real-World Impact**: Reduces response time from hours to minutes
- **Scalability**: Designed for global supply chain operations
- **Business Value**: Prevents millions in losses from delayed or spoiled shipments

## 🔒 Assumptions & Limitations

### Assumptions

1. **Mock Data**: Demo uses pre-generated disruptions, routes, and shipments
2. **In-Memory Storage**: Data is not persisted between restarts
3. **Simplified Routing**: Alternative route selection uses basic criteria
4. **Cost Estimation**: Cost impacts are simplified calculations
5. **AI Service**: Currently uses template-based responses (can be upgraded to LLM)

### Known Limitations

1. **No Authentication**: No user login or role-based access control
2. **No Real-Time Updates**: Disruption feed requires manual refresh
3. **No Database**: All data stored in memory (resets on restart)
4. **No External Integrations**: No connection to real logistics APIs
5. **Simplified Decision Logic**: Production systems would need more complex rules

### Future Enhancements

- Real-time disruption monitoring via external APIs
- Persistent database (PostgreSQL/MongoDB)
- User authentication and role management
- Advanced ML-based impact prediction
- Integration with logistics platforms (SAP, Oracle)
- Mobile application
- Voice interface using speech recognition

## 🏆 Build2Break Hackathon Compliance

### ✅ Deployment
- Docker Compose for single-command deployment
- No manual configuration required
- All dependencies containerized

### ✅ Documentation
- Clear problem statement and domain alignment
- Complete setup instructions
- Architecture overview
- Assumptions and limitations documented

### ✅ Evaluation Criteria

**Solution Quality (5 pts):**
- End-to-end disruption response workflow
- AI-guided decision process
- Clear action tickets with explanations

**Impact (5 pts):**
- Addresses real LogiTech problem
- Reduces response time significantly
- Prevents costly delays and losses

**Reliability (5 pts):**
- Deterministic decision engine
- Comprehensive error handling
- Input validation with Pydantic

**Technical Alignment (5 pts):**
- Modern tech stack (FastAPI, Docker)
- Clean service separation
- RESTful API design
- No platform-specific dependencies

## 👥 Team

- **Domain**: LogiTech (Logistics & Supply Chain)
- **Project Type**: Web Application
- **Deployment**: Docker Compose

## 📄 License

This project is created for the Build2Break hackathon.

---

**Built with ❤️ for Build2Break Hackathon**
