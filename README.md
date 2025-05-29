# Agent Conversational Compass

A production-ready conversational AI customer service platform featuring intelligent memory management, real-time database integration, and secure multi-user access controls. Built with session-based conversation tracking, PostgreSQL backend, and OpenAI GPT-4o-mini integration.

## 🚀 Key Features

### 🧠 **Intelligent Memory System**
- **Session-Based Conversation Tracking**: Maintains context within individual chat sessions
- **Cross-Session User History**: Remembers user interactions across different sessions
- **Vector Database Storage**: Qdrant-powered semantic search through conversation history
- **Real-Time Context**: AI maintains conversation continuity and references past interactions

### 🗄️ **Real Database Integration**
- **PostgreSQL Backend**: Comprehensive e-commerce database with customers, orders, products, shipments
- **MCP Server Architecture**: Model Context Protocol for secure database operations
- **Order Management**: Real-time order lookup, tracking, and history retrieval
- **No AI Hallucination**: All order data comes from actual database records

### 🔐 **Security & Authorization**
- **Role-Based Access Control**: Customers can only access their own data
- **Agent Authorization**: Customer service agents can access any customer's information
- **Unauthorized Access Prevention**: Security logging and access attempt blocking
- **Data Privacy Protection**: GDPR-compliant customer data handling

### 📋 **Customer Service Features**
- **Order History Retrieval**: "Show me order history for customer123"
- **Order Status Lookup**: Real-time order tracking and shipping information
- **Customer Profile Access**: Secure customer information retrieval
- **Support Ticket Management**: Integrated support ticket system
- **Payment Transaction Tracking**: Comprehensive payment and refund history

### 🤖 **AI-Powered Interactions**
- **OpenAI GPT-4o-mini**: Advanced language model for intelligent responses
- **Sentiment Analysis**: Real-time sentiment tracking using RoBERTa
- **Fallback Responses**: Rule-based responses when AI is unavailable
- **Context-Aware**: Uses real data to provide accurate, helpful responses

## 🛠 Tech Stack

### Core Architecture
- **Backend**: Python 3.12 + FastAPI with async support
- **Frontend**: React 18.3.1 + TypeScript + Tailwind CSS + Vite
- **AI Integration**: OpenAI GPT-4o-mini with function calling
- **Memory**: Qdrant vector database for conversation storage
- **Database**: PostgreSQL 15 for business data (customers, orders, products)
- **Orchestration**: LangGraph for AI agent workflow management

### Specialized Services
- **MCP Server**: Model Context Protocol dispatcher for database operations
- **Worker Service**: Async task processing and background jobs
- **Sentiment Analysis**: RoBERTa model for emotion detection
- **Embeddings**: CLIP for multimodal text/image embeddings
- **Payment Integration**: Stripe webhook processing

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Service Orchestration**: 6-service architecture with health checks
- **Environment Management**: Development and production configurations
- **Monitoring**: Comprehensive logging and health monitoring

## 📊 Architecture Diagrams

### System Architecture Overview

The following diagrams illustrate the complete system architecture, data flow, and memory management patterns:

#### 🏗️ **Complete System Architecture**
- **Mermaid**: [`diagrams/architecture.mermaid`](diagrams/architecture.mermaid)
- **PlantUML**: [`diagrams/architecture.plantuml`](diagrams/architecture.plantuml)

Shows the complete 6-service containerized architecture including:
- Frontend Layer (React + TypeScript)
- API Gateway (FastAPI + Security Middleware)
- AI Processing Layer (LangGraph + OpenAI + Sentiment Analysis)
- Data Processing Layer (MCP Server + Database Tools)
- Data Storage Layer (PostgreSQL + Qdrant)
- Background Services (Worker Service)
- Security & Authorization (Role-based access control)

![System Architecture](diagrams/architecture.svg)

#### 🔄 **Data Flow & Conversation Processing**
- **Mermaid**: [`diagrams/dataflow.mermaid`](diagrams/dataflow.mermaid)
- **PlantUML**: [`diagrams/dataflow.plantuml`](diagrams/dataflow.plantuml)

Detailed sequence diagram showing:
- User query processing from frontend to backend
- Security authorization checks and role-based access
- AI processing with LangGraph nodes (Action, Policy, Sentiment)
- Database queries through MCP server to PostgreSQL
- Memory management with Qdrant vector storage
- OpenAI GPT-4o-mini integration for intelligent responses
- Complete conversation storage and context building

![Data Flow Architecture](diagrams/dataflow.svg)

#### 🧠 **Memory Management Architecture**
- **Mermaid**: [`diagrams/memory-architecture.mermaid`](diagrams/memory-architecture.mermaid)
- **PlantUML**: [`diagrams/memory-architecture.plantuml`](diagrams/memory-architecture.plantuml)

Comprehensive memory system showing:
- **Session Memory**: Temporary conversation context within sessions
- **User Memory**: Persistent cross-session user history and profiles
- **Semantic Memory**: Vector embeddings for pattern matching and search
- **Business Memory**: Real-time PostgreSQL data integration
- **Memory Processing**: Context assembly, filtering, and prioritization
- **Security Integration**: Role-based memory access and audit logging

![Memory Architecture](diagrams/memory-architecture.svg)

#### 🐳 **Docker Services Architecture**
- **Mermaid**: [`diagrams/docker-services.mermaid`](diagrams/docker-services.mermaid)

Complete containerized environment showing:
- **6 Core Services**: PostgreSQL, Qdrant, MCP Server, Backend, Frontend, Worker
- **Service Dependencies**: Health checks and inter-service communication
- **Volume Management**: Persistent data storage for databases
- **Network Configuration**: Internal service discovery and port mappings
- **Development Setup**: Code mounting and hot-reload capabilities

### Architecture Highlights

![Architecture Overview](diagrams/architecture.svg)

*Click on the architecture diagram above to see the complete 6-service system with all components, data flows, and security layers.*

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### 1. Clone Repository
```bash
git clone <repository-url>
cd agent-conversational-compass
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key to .env:
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 3. Start All Services
```bash
# Start complete environment (6 services)
make dev
```

### 4. Access Applications
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001
- **Worker Service**: http://localhost:8002
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **PostgreSQL**: localhost:5432

## 🎯 Usage Examples

### Customer Service Agent Queries
```bash
# Get order history for any customer (authorized agent)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "customer_service_agent",
    "message": "Show me order history for customer123",
    "session_id": "agent_session_1"
  }'

# Look up specific order details
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "support_agent",
    "message": "What is the status of order #123?",
    "session_id": "support_session_1"
  }'
```

### Customer Self-Service
```bash
# Customer accessing their own order history
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "customer123",
    "message": "Show me my order history",
    "session_id": "customer_session_1"
  }'

# Customer checking order status
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user@email.com",
    "message": "What is the status of my order #123?",
    "session_id": "customer_session_2"
  }'
```

### Security Examples
```bash
# This will be BLOCKED - customer trying to access another's data
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "customer1",
    "message": "Show me order history for customer123",
    "session_id": "unauthorized_attempt"
  }'
# Response: "I'm sorry, but I cannot provide order history for other customers..."
```

## 🏗 Detailed Architecture

### Service Architecture
The system consists of 6 containerized services:

1. **PostgreSQL Database**: Business data (customers, orders, products, shipments)
2. **Qdrant Vector Database**: Conversation memory and semantic search
3. **MCP Server**: Database operations and tool dispatch
4. **Backend API**: Main application logic and AI orchestration
5. **Frontend Dashboard**: React-based user interface
6. **Worker Service**: Background task processing

### Data Flow Architecture

![Complete Data Flow](diagrams/dataflow.svg)

*The diagram above shows the complete conversation flow from user input through security checks, AI processing, database queries, memory management, and response generation.*

### Memory Architecture

![Memory Management System](diagrams/memory-architecture.svg)

*This diagram illustrates the sophisticated memory management system with session tracking, cross-session user history, semantic search, and business data integration.*

## 🔐 Security Model

### Authorization Levels
- **Customers**: Can only access their own order history and personal data
- **Customer Service Agents**: Can access any customer's data for support purposes
- **Admins**: Full system access with additional privileges

### Supported Agent Roles
- `customer_service_agent`
- `support_agent`
- `admin`
- `cs_agent`
- `agent`

### Security Features
- Input validation and SQL injection prevention
- Role-based data access controls
- Comprehensive audit logging
- Unauthorized access attempt detection
- Session-based authentication context

## 🗄️ Database Schema

### Core Tables
- **customers**: Customer profiles and contact information
- **orders**: Order records with status and payment information
- **order_items**: Individual items within orders
- **products**: Product catalog with pricing and descriptions
- **shipments**: Shipping tracking and delivery information
- **support_tickets**: Customer support case management
- **payment_transactions**: Payment processing history
- **refunds**: Refund processing and tracking

### Sample Data
The system includes comprehensive seed data:
- 7 sample customers including "customer123" (Test User)
- Multiple orders with different statuses (shipped, delivered, processing, cancelled)
- Real product catalog (electronics, clothing, books, etc.)
- Complete shipping and payment transaction history

## 🧪 Testing the System

### Order History Tests
```bash
# Test customer accessing own data (ALLOWED)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "customer123", "message": "Show me my orders", "session_id": "test1"}'

# Test agent accessing customer data (ALLOWED)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "customer_service_agent", "message": "Order history for customer1", "session_id": "test2"}'

# Test unauthorized access (BLOCKED)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "customer1", "message": "Show me customer123 orders", "session_id": "test3"}'
```

### Database Integration Tests
```bash
# Test specific order lookup
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "test_user@email.com", "message": "Status of order #123?", "session_id": "test4"}'

# Test customer lookup by email
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "support_agent", "message": "Order history for jane.smith@email.com", "session_id": "test5"}'
```

## 🐳 Docker Services

### Service Configuration
```yaml
services:
  postgres:      # Business database
  qdrant:        # Vector memory
  mcp_server:    # Database tools
  backend:       # Main API
  frontend:      # React UI
  worker:        # Background tasks
```

### Health Checks
All services include comprehensive health checks:
```bash
# Check all service health
make health

# Individual service logs
docker-compose logs backend --tail=20
docker-compose logs mcp_server --tail=20
```

## 📊 Development Commands

```bash
# Core operations
make dev          # Start all services
make dev-local    # Local development mode
make health       # Check service health
make logs         # View all logs
make clean        # Clean containers

# Testing
make test-mcp     # Test MCP server
make test-chat    # Test chat functionality
make test-db      # Test database integration

# Production
make build-prod   # Build production images
make deploy       # Production deployment
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database
DATABASE_URL=postgresql://cs_user:cs_password@postgres:5432/customer_service

# Services
QDRANT_URL=http://qdrant:6333
MCP_SERVER_URL=http://mcp_server:8001
WORKER_URL=http://worker:8002

# Frontend (for Docker)
VITE_API_BASE_URL=http://localhost:8000
VITE_MCP_BASE_URL=http://localhost:8001
VITE_WORKER_BASE_URL=http://localhost:8002

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Customer Mapping
The system supports friendly customer identifiers:
- `customer123` → Test User (test_user@email.com)
- `customer1` → John Doe (john.doe@email.com)
- `customer2` → Jane Smith (jane.smith@email.com)
- And more...

### Port Configuration
The system uses the following port mappings:
- **Frontend**: `5173:8080` (host:container) - Vite dev server runs on port 8080 inside container
- **Backend**: `8000:8000` - FastAPI backend
- **MCP Server**: `8001:8001` - Model Context Protocol server
- **Worker**: `8002:8002` - Background worker service
- **Qdrant**: `6333:6333` - Vector database
- **PostgreSQL**: `5432:5432` - Business database

## 🚀 Production Deployment

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
1. Set production environment variables
2. Configure SSL certificates
3. Set up database backups
4. Configure monitoring and logging
5. Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run linting: `make lint`
5. Test functionality: `make test`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push and create Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **OpenAI** for GPT-4o-mini and embeddings API
- **Qdrant** for vector database technology
- **FastAPI** for high-performance Python web framework
- **LangGraph** for agent workflow orchestration
- **React** and **Vite** for modern frontend development
- **PostgreSQL** for reliable business data storage
