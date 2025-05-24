
# Customer Service Agentic Workflow SaaS

A production-ready SaaS platform that delivers intelligent customer service through an agentic workflow powered by LangGraph, OpenAI, and semantic search.

## Features

- **AI-Powered Customer Service**: Natural language understanding and contextual responses
- **Multimodal Semantic Search**: CLIP embeddings for text and image search
- **Agent Memory**: Long-term conversation memory stored in Qdrant vector database
- **Payment Processing**: Integrated Stripe payment gateway
- **Real-time Dashboard**: GenUI dashboard with sentiment analysis and payment tracking
- **Live Agent Assistance**: Copilotkit integration for support staff
- **Microservices Architecture**: MCP Server pattern with async worker processes

## Tech Stack

- **Backend**: Python 3.12, FastAPI, LangGraph
- **AI/ML**: OpenAI ChatGPT o1, CLIP embeddings, RoBERTa sentiment analysis
- **Database**: Qdrant vector database
- **Payments**: Stripe API
- **Frontend**: React, TypeScript, Copilotkit
- **Infrastructure**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd customer-service-saas
cp .env.example .env
# Edit .env with your API keys
```

2. **Start all services**:
```bash
docker compose up -d
```

3. **Initialize Qdrant collections**:
```bash
./infra/qdrant_init.sh
```

4. **Access the application**:
- Frontend Dashboard: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Development

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)
- Node.js 18+ (for frontend development)

### Local Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
uvicorn main:app --reload --port 8000

# Frontend development
cd frontend
npm install
npm run dev
```

### Available Commands

```bash
make dev      # Start development environment
make test     # Run all tests
make lint     # Run linting and formatting
make deploy   # Deploy to production
```

## API Usage

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user": "customer123", "message": "I need help with payment for invoice #123"}'
```

### Semantic Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "payment issues", "limit": 5}'
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Qdrant        │
│   Dashboard     │◄──►│   FastAPI       │◄──►│   Vector DB     │
│   (React)       │    │   + LangGraph   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MCP Server    │    │   Worker        │
                       │   Dispatcher    │◄──►│   LangGraph     │
                       │                 │    │   Tasks         │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Stripe        │
                       │   Payment       │
                       │   Gateway       │
                       └─────────────────┘
```

## Environment Variables

See `.env.example` for all required environment variables.

## Deployment

### Docker Deployment
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment (Render/Fly.io)
1. Set environment variables in your platform
2. Deploy using the provided Dockerfile
3. Ensure Qdrant service is accessible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make lint` and `make test`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
