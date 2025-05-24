
.PHONY: help dev test lint clean build deploy setup

# Default target
help:
	@echo "Customer Service Agentic Workflow - Available Commands:"
	@echo ""
	@echo "  setup      - Initial project setup"
	@echo "  dev        - Start development environment"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linting and formatting"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  build      - Build all Docker images"
	@echo "  deploy     - Deploy to production"
	@echo "  logs       - Show service logs"
	@echo "  shell      - Open backend shell"
	@echo ""

# Initial setup
setup:
	@echo "Setting up Customer Service Agentic Workflow..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please update with your API keys"; fi
	@chmod +x infra/qdrant_init.sh
	@echo "Setup complete! Update .env with your API keys, then run 'make dev'"

# Development environment
dev:
	@echo "Starting development environment..."
	@docker compose up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Initializing Qdrant collections..."
	@./infra/qdrant_init.sh
	@echo ""
	@echo "Development environment ready!"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Qdrant: http://localhost:6333"
	@echo ""
	@echo "Run 'make logs' to see service logs"

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

# Show logs
logs:
	@docker compose logs -f

# Open backend shell
shell:
	@docker compose exec backend bash

# Production deployment
deploy:
	@echo "Deploying to production..."
	@echo "This would typically:"
	@echo "  1. Build production images"
	@echo "  2. Push to registry"
	@echo "  3. Deploy to production environment"
	@echo "  4. Run health checks"
	@echo ""
	@echo "Configure your production deployment in this target"

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

# Health check all services
health:
	@echo "Checking service health..."
	@echo "Backend:"
	@curl -s http://localhost:8000/health | python3 -m json.tool
	@echo ""
	@echo "Qdrant:"
	@curl -s http://localhost:6333/health
	@echo ""
	@echo "Frontend (simple check):"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/

# Monitor services
monitor:
	@echo "Monitoring services..."
	@watch -n 2 'echo "=== Service Status ===" && docker compose ps && echo "" && echo "=== Health Checks ===" && curl -s http://localhost:8000/health | python3 -m json.tool'
