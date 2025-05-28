# Customer Service AI Dashboard

A production-ready customer service platform powered by AI agents, featuring intelligent conversation handling, semantic search, sentiment analysis, and real-time analytics with full containerization and MCP (Model Context Protocol) server integration.

## 🚀 Features

- **AI-Powered Customer Service**: Natural language understanding with OpenAI integration and fallback responses
- **MCP Server Integration**: Model Context Protocol for task queuing and inter-service communication
- **Multimodal Semantic Search**: CLIP embeddings for text and image search through conversation history
- **Real-time Dashboard**: Modern React dashboard with system health monitoring and analytics
- **Sentiment Analysis**: Real-time sentiment tracking using RoBERTa model
- **Vector Database**: Qdrant for conversation storage and semantic search
- **Payment Integration**: Stripe webhook integration for payment event tracking
- **Containerized Architecture**: Full Docker containerization with development and production configurations
- **Async Task Processing**: Background worker service for heavy computational tasks
- **Responsive UI**: Clean, modern interface with multiple dashboard views

## 🛠 Tech Stack

### Backend Services
- **Python 3.12**: FastAPI framework with async support
- **LangGraph**: Agent workflow orchestration
- **OpenAI**: GPT models for conversation handling
- **Qdrant**: Vector database for embeddings and search
- **CLIP**: Multimodal embeddings for text/image search
- **RoBERTa**: Sentiment analysis model
- **Stripe**: Payment processing integration
- **MCP Server**: Model Context Protocol dispatcher
- **Worker Service**: Async task processor

### Frontend
- **React 18**: Modern React with hooks and TypeScript
- **Vite**: Fast development server and build tool
- **Recharts**: Data visualization and analytics charts
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **React Query**: Server state management

### Infrastructure
- **Docker**: Containerized services with multi-stage builds
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and static file serving
- **Health Checks**: Comprehensive service monitoring

## 🚀 Quick Start (Containerized)

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd agent-conversational-compass
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_api_key_here
# STRIPE_API_KEY=your_stripe_api_key_here
# STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### 3. Start All Services
```bash
# Start complete containerized environment
make dev
```

This will start:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **MCP Server**: http://localhost:8001
- **Worker Service**: http://localhost:8002
- **Qdrant Database**: http://localhost:6333

### 4. Access the Application
- **Frontend Dashboard**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **MCP Server Health**: http://localhost:8001/health
- **Worker Health**: http://localhost:8002/health
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 🐳 Docker Setup

For detailed containerization instructions, see [DOCKER_SETUP.md](./DOCKER_SETUP.md).

### Development Commands
```bash
make dev          # Start all services in containers
make dev-local    # Start only Qdrant, run services locally
make logs         # View all service logs
make health       # Check all service health
make test-mcp     # Test MCP server functionality
make test-worker  # Test worker service
make clean        # Clean up containers and volumes
```

### Production Deployment
```bash
make build-prod   # Build production images
make deploy       # Deploy to production
```

## 🔄 MCP Server Integration

The MCP (Model Context Protocol) server provides centralized task management and inter-service communication:

### Task Queue Management
```typescript
import { queueTask } from './config/api';

// Queue conversation analysis
# Start backend (in one terminal)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
uvicorn main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- **Frontend Dashboard**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📱 Dashboard Features

### Main Dashboard
- **System Health Monitoring**: Real-time status of all services
- **Recent Conversations**: Latest customer interactions with status
- **Sentiment Analytics**: 7-day sentiment trend visualization
- **Payment Events**: Recent Stripe payment activities

### Chat Interface
- **Real-time Messaging**: Direct customer service chat
- **Sentiment Analysis**: Live sentiment scoring for each message
- **Action Detection**: Automatic categorization of customer requests
- **Conversation History**: Persistent chat storage in Qdrant

### Semantic Search
- **Conversation Search**: Find relevant past interactions
- **Multimodal Support**: Search through text and image content
- **Relevance Scoring**: AI-powered result ranking
- **Filter Options**: Customize search parameters

### Analytics Dashboard
- **Performance Metrics**: Response times, resolution rates
- **Sentiment Trends**: Historical sentiment analysis
- **Volume Analytics**: Conversation patterns and peak times
- **Customer Satisfaction**: Satisfaction scoring and trends

## 🔧 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "customer123", 
    "message": "I need help with my payment"
  }'
```

### Semantic Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "payment issues", 
    "limit": 5,
    "include_images": true
  }'
```

### Analytics
```bash
curl http://localhost:8000/analytics/sentiment
```

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React         │    │   FastAPI       │    │   Qdrant        │
│   Dashboard     │◄──►│   Backend       │◄──►│   Vector DB     │
│   (Port 8080)   │    │   (Port 8000)   │    │   (Port 6333)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   LangGraph     │    │   OpenAI        │
                       │   Agent         │◄──►│   GPT Models    │
                       │   Workflow      │    │                 │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CLIP          │    │   Stripe        │
                       │   Embeddings    │    │   Webhooks      │
                       │   + RoBERTa     │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
pip install -e .

# Run with auto-reload
uvicorn main:app --reload --port 8000

# Run tests
pytest

# Format code
black .
isort .
```

### Frontend Development
```bash
cd frontend
npm install

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Available Make Commands
```bash
make dev      # Start development environment
make test     # Run all tests
make lint     # Run linting and formatting
make clean    # Clean up containers and volumes
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Environment Variables

### Backend (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=http://localhost:6333

# Optional
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend
The frontend uses environment variables to configure the backend API connection.

```bash
# Backend API URL - defaults to http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000
```

**Configuration Options:**
- Development: `VITE_API_BASE_URL=http://localhost:8000`
- Custom port: `VITE_API_BASE_URL=http://localhost:3001`
- Production: `VITE_API_BASE_URL=https://api.yourdomain.com`
- Docker: `VITE_API_BASE_URL=http://backend:8000`

**Setting the variable:**
```bash
# Option 1: Create .env file in frontend/ directory
echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env

# Option 2: Set when running
VITE_API_BASE_URL=http://localhost:3001 npm run dev

# Option 3: Export environment variable
export VITE_API_BASE_URL=http://localhost:3001
```

See `frontend/CONFIG.md` for detailed configuration instructions.

## 🚨 Troubleshooting

### Common Issues

1. **Blank Frontend Page**
   - Ensure no external scripts are interfering
   - Check browser console for JavaScript errors
   - Verify Vite dev server is running on port 8080

2. **Backend Connection Issues**
   - Verify Qdrant is running: `docker ps | grep qdrant`
   - Check backend logs for connection errors
   - Ensure CORS is configured for frontend port

3. **OpenAI API Errors**
   - Verify API key is set in backend/.env
   - Check API quota and billing status
   - Fallback responses will be used if API is unavailable

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Check Qdrant directly
curl http://localhost:6333/collections

# Check frontend
curl http://localhost:8080
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Run linting: `make lint`
5. Run tests: `make test`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- Qdrant for vector database technology
- FastAPI for the excellent Python web framework
- React and Vite for modern frontend development
