# Docker Containerized Setup Guide

This guide explains how to run the Customer Service Agentic Workflow using Docker containers with full MCP server integration.

## Architecture Overview

The containerized setup includes:

- **Frontend**: React application with Vite (port 5173)
- **Backend**: FastAPI service (port 8000)
- **MCP Server**: Model Context Protocol dispatcher (port 8001)
- **Worker**: Async task processor (port 8002)
- **Qdrant**: Vector database (port 6333)

## Quick Start

### 1. Environment Setup

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Update the `.env` file with your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_API_KEY=your_stripe_api_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Optional (defaults provided)
QDRANT_URL=http://qdrant:6333
CLIP_MODEL=openai/clip-vit-base-patch32
ENVIRONMENT=development
```

### 2. Start Development Environment

```bash
make dev
```

This will:
- Build all Docker images
- Start all services
- Initialize Qdrant collections
- Display service URLs

### 3. Access Services

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001
- **Worker Service**: http://localhost:8002
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Service Details

### Frontend (React + Vite)

**Container**: `frontend`
**Port**: 5173
**Features**:
- Hot reloading in development
- Nginx proxy for production
- API routing to backend services
- MCP server integration

**Environment Variables**:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MCP_BASE_URL=http://localhost:8001
VITE_WORKER_BASE_URL=http://localhost:8002
```

### Backend (FastAPI)

**Container**: `backend`
**Port**: 8000
**Features**:
- Customer service chat API
- Semantic search
- Analytics endpoints
- Stripe integration

**Health Check**: `GET /health`

### MCP Server (Model Context Protocol)

**Container**: `mcp_server`
**Port**: 8001
**Features**:
- Task queue management
- Webhook processing
- Notification system
- Inter-service communication

**Key Endpoints**:
- `GET /health` - Health check
- `POST /_queue` - Queue tasks
- `POST /webhook` - Process webhooks
- `POST /notify` - Send notifications

### Worker Service

**Container**: `worker`
**Port**: 8002
**Features**:
- Async task processing
- Conversation analysis
- Payment processing
- Background maintenance

**Key Endpoints**:
- `GET /health` - Health check
- `POST /process` - Process tasks

### Qdrant (Vector Database)

**Container**: `qdrant`
**Ports**: 6333 (HTTP), 6334 (gRPC)
**Features**:
- Vector storage and search
- Conversation embeddings
- Semantic similarity

## Development Workflows

### Container Development

Start all services in containers:
```bash
make dev
```

View logs:
```bash
make logs                # All services
make backend-logs        # Backend only
make mcp-logs           # MCP server only
make worker-logs        # Worker only
```

### Local Development

For faster iteration, run services locally:
```bash
make dev-local
```

Then start services manually:
```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - MCP Server
cd mcp_server && uvicorn dispatcher:app --reload --port 8001

# Terminal 3 - Worker
cd worker && uvicorn worker:app --reload --port 8002

# Terminal 4 - Frontend
cd frontend && npm run dev
```

### Testing Services

Test all services:
```bash
make health              # Health checks
make test-chat          # Chat endpoint
make test-mcp           # MCP server
make test-worker        # Worker service
```

## MCP Server Integration

The MCP (Model Context Protocol) server acts as a central dispatcher for:

### Task Queue Management

Queue tasks from the frontend:
```typescript
import { queueTask } from './config/api';

// Queue a conversation analysis task
await queueTask('conversation_analysis', {
  user_id: 'user123',
  conversation_data: { messages: ['Hello', 'I need help'] }
});
```

### Webhook Processing

Process webhooks from external services:
```bash
curl -X POST http://localhost:8001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "stripe",
    "event_type": "payment_intent.succeeded",
    "data": {"id": "pi_123", "amount": 2000}
  }'
```

### Inter-Service Communication

Services communicate through the MCP server:
- Frontend → MCP Server → Worker
- Backend → MCP Server → External APIs
- Worker → MCP Server → Backend

## Production Deployment

### Build Production Images

```bash
make build-prod
```

### Deploy to Production

```bash
make deploy
```

This uses `docker-compose.prod.yml` with:
- Optimized production builds
- Resource limits
- Health checks
- Nginx reverse proxy

### Environment Configuration

For production, update these variables:
```env
ENVIRONMENT=production
API_URL=https://api.yourdomain.com
MCP_URL=https://mcp.yourdomain.com
WORKER_URL=https://worker.yourdomain.com
DOCKER_REGISTRY=your-registry.com
IMAGE_TAG=v1.0.0
```

## Monitoring and Debugging

### Service Monitoring

```bash
make monitor             # Real-time monitoring
make health             # Health check all services
```

### Container Access

```bash
make shell              # Backend shell
make mcp-shell          # MCP server shell
make worker-shell       # Worker shell
```

### Log Analysis

```bash
# Follow logs for specific service
docker compose logs -f backend
docker compose logs -f mcp_server
docker compose logs -f worker

# Search logs
docker compose logs backend | grep ERROR
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   lsof -i :8000
   lsof -i :8001
   lsof -i :8002
   ```

2. **Service Dependencies**
   ```bash
   # Restart in correct order
   make stop
   make dev
   ```

3. **Database Issues**
   ```bash
   # Reset Qdrant
   make db-reset
   ```

4. **Container Issues**
   ```bash
   # Clean rebuild
   make clean
   make build
   make dev
   ```

### Health Checks

All services include health endpoints:
- Backend: `http://localhost:8000/health`
- MCP Server: `http://localhost:8001/health`
- Worker: `http://localhost:8002/health`
- Qdrant: `http://localhost:6333/health`

### Performance Tuning

Adjust resource limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use secrets management in production
3. **Network Security**: Use internal networks for service communication
4. **Container Security**: Run as non-root users
5. **SSL/TLS**: Enable HTTPS in production

## Next Steps

1. Configure your API keys in `.env`
2. Run `make dev` to start the development environment
3. Access the dashboard at http://localhost:5173
4. Test MCP integration in the "MCP Server" tab
5. Monitor logs with `make logs`

For more details, see the main README.md file. 