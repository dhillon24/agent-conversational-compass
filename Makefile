.PHONY: help dev test lint clean build deploy setup

# Default target
help:
	@echo "Customer Service Agentic Workflow - Available Commands:"
	@echo ""
	@echo "  setup      - Initial project setup"
	@echo "  dev        - Start development environment (containerized)"
	@echo "  dev-local  - Start local development (non-containerized)"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linting and formatting"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  build      - Build all Docker images"
	@echo "  deploy     - Deploy to production"
	@echo "  logs       - Show service logs"
	@echo "  shell      - Open backend shell"
	@echo "  mcp-logs   - Show MCP server logs"
	@echo "  worker-logs - Show worker logs"
	@echo ""

# Initial setup
setup:
	@echo "Setting up Customer Service Agentic Workflow..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please update with your API keys"; fi
	@chmod +x infra/qdrant_init.sh
	@echo "Setup complete! Update .env with your API keys, then run 'make dev'"

# Development environment (containerized)
dev:
	@echo "Starting containerized development environment..."
	@docker compose up -d
	@echo "Waiting for services to start..."
	@sleep 15
	@echo "Initializing Qdrant collections..."
	@./infra/qdrant_init.sh
	@echo ""
	@echo "Development environment ready!"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - MCP Server: http://localhost:8001"
	@echo "  - Worker Service: http://localhost:8002"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Qdrant: http://localhost:6333"
	@echo ""
	@echo "Run 'make logs' to see service logs"

# Local development (non-containerized)
dev-local:
	@echo "Starting local development environment..."
	@echo "Starting Qdrant..."
	@docker compose up -d qdrant
	@sleep 5
	@./infra/qdrant_init.sh
	@echo ""
	@echo "Start the following services manually:"
	@echo "  Backend: cd backend && uvicorn main:app --reload --port 8000"
	@echo "  MCP Server: cd mcp_server && uvicorn dispatcher:app --reload --port 8001"
	@echo "  Worker: cd worker && uvicorn worker:app --reload --port 8002"
	@echo "  Frontend: cd frontend && npm run dev"

# Run all tests
test:
	@echo "Running all tests..."
	@echo "Testing backend..."
	@cd backend && python -m pytest tests/ -v
	@echo "Testing frontend..."
	@cd frontend && npm test
	@echo "All tests completed!"

# Linting and formatting
lint:
	@echo "Running linting and formatting..."
	@echo "Backend (Python)..."
	@cd backend && black . && ruff check . && mypy . --ignore-missing-imports
	@echo "MCP Server (Python)..."
	@cd mcp_server && black . && ruff check .
	@echo "Worker (Python)..."
	@cd worker && black . && ruff check .
	@echo "Frontend (TypeScript)..."
	@cd frontend && npm run lint
	@echo "Linting completed!"

# Clean up
clean:
	@echo "Cleaning up containers and volumes..."
	@docker compose down -v
	@docker system prune -f
	@echo "Cleanup completed!"

# Build all images
build:
	@echo "Building all Docker images..."
	@docker compose build
	@echo "Build completed!"

# Build production images
build-prod:
	@echo "Building production images..."
	@docker build -t customer-service-backend:latest ./backend
	@docker build -t customer-service-frontend:latest ./frontend
	@docker build -t customer-service-mcp:latest ./mcp_server
	@docker build -t customer-service-worker:latest ./worker
	@echo "Production images built!"

# Show logs
logs:
	@docker compose logs -f

# Show specific service logs
backend-logs:
	@docker compose logs -f backend

frontend-logs:
	@docker compose logs -f frontend

mcp-logs:
	@docker compose logs -f mcp_server

worker-logs:
	@docker compose logs -f worker

# Open backend shell
shell:
	@docker compose exec backend bash

# Open MCP server shell
mcp-shell:
	@docker compose exec mcp_server bash

# Open worker shell
worker-shell:
	@docker compose exec worker bash

# Production deployment
deploy:
	@echo "Deploying to production..."
	@echo "Building production images..."
	@make build-prod
	@echo "Starting production environment..."
	@docker compose -f docker-compose.prod.yml up -d
	@echo "Waiting for services to start..."
	@sleep 20
	@echo "Initializing Qdrant collections..."
	@./infra/qdrant_init.sh
	@echo ""
	@echo "Production deployment complete!"
	@echo "  - Frontend: http://localhost"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - MCP Server: http://localhost:8001"

# Database operations
db-init:
	@echo "Initializing Qdrant collections..."
	@./infra/qdrant_init.sh

db-reset:
	@echo "Resetting Qdrant collections..."
	@docker compose restart qdrant
	@sleep 5
	@./infra/qdrant_init.sh

# Quick test of the chat endpoint
test-chat:
	@echo "Testing chat endpoint..."
	@curl -X POST http://localhost:8000/chat \
		-H "Content-Type: application/json" \
		-d '{"user": "test_user", "message": "I need help with payment for invoice #123"}' \
		| python3 -m json.tool

# Test MCP server
test-mcp:
	@echo "Testing MCP server..."
	@curl -X GET http://localhost:8001/health | python3 -m json.tool
	@echo ""
	@echo "Testing task queue..."
	@curl -X POST http://localhost:8001/_queue \
		-H "Content-Type: application/json" \
		-d '{"task_type": "test_task", "payload": {"test": "data"}, "priority": 1}' \
		| python3 -m json.tool

# Test worker
test-worker:
	@echo "Testing worker service..."
	@curl -X GET http://localhost:8002/health | python3 -m json.tool
	@echo ""
	@echo "Testing task processing..."
	@curl -X POST http://localhost:8002/process \
		-H "Content-Type: application/json" \
		-d '{"task_type": "conversation_analysis", "payload": {"user_id": "test", "conversation_data": {"messages": ["Hello"]}}}' \
		| python3 -m json.tool

# Health check all services
health:
	@echo "Checking service health..."
	@echo "Backend:"
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo ""
	@echo "MCP Server:"
	@curl -s http://localhost:8001/health | python3 -m json.tool
	@echo ""
	@echo "Worker:"
	@curl -s http://localhost:8002/health | python3 -m json.tool
	@echo ""
	@echo "Qdrant:"
	@curl -s http://localhost:6333/health
	@echo ""
	@echo "Frontend (simple check):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/

# Monitor services
monitor:
	@echo "Monitoring services..."
	@watch -n 2 'echo "=== Service Status ===" && docker compose ps && echo "" && echo "=== Health Checks ===" && curl -s http://localhost:8000/health | python3 -m json.tool && echo "" && curl -s http://localhost:8001/health | python3 -m json.tool && echo "" && curl -s http://localhost:8002/health | python3 -m json.tool'

# Stop all services
stop:
	@echo "Stopping all services..."
	@docker compose down

# Restart all services
restart:
	@echo "Restarting all services..."
	@docker compose restart

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	@cd backend && pip-compile requirements.in
	@cd mcp_server && pip-compile requirements.in
	@cd worker && pip-compile requirements.in
	@cd frontend && npm update
	@echo "Dependencies updated!"
