import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
from dotenv import load_dotenv

from graph.build_graph import build_customer_service_graph
from services.qdrant_client import QdrantService
from services.stripe_client import StripeService
from services.embeddings import EmbeddingService
from services.mcp_client import mcp_client

# Load environment variables from .env file in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
qdrant_service = QdrantService()
embedding_service = EmbeddingService()
stripe_service = StripeService()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Build the LangGraph workflow
customer_service_graph = build_customer_service_graph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    logger.info("Starting Customer Service SaaS backend...")
    
    # Initialize Qdrant collections
    await qdrant_service.initialize_collections()
    
    # Initialize embedding service
    await embedding_service.initialize()
    
    # Initialize MCP client
    await mcp_client.initialize()
    
    logger.info("All services initialized successfully")
    yield
    
    # Cleanup
    await mcp_client.close()
    logger.info("Shutting down services...")


app = FastAPI(
    title="Customer Service Agentic Workflow",
    description="AI-powered customer service with semantic search and payment processing",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    user: str
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    response: str
    sentiment: Dict[str, float]
    actions_taken: list
    session_id: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    include_images: bool = True


class SearchResponse(BaseModel):
    results: list
    total_count: int


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Customer Service Agentic Workflow API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Qdrant connection
        qdrant_status = await qdrant_service.health_check()
        
        # Check OpenAI availability
        embedding_status = await embedding_service.health_check()
        
        # Check MCP server connection
        mcp_status = await mcp_client.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "qdrant": qdrant_status,
                "embeddings": embedding_status,
                "mcp_server": mcp_status,
                "stripe": "connected" if stripe.api_key else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint that processes customer messages through the LangGraph workflow."""
    try:
        logger.info(f"Processing chat request from user: {request.user}")
        
        # Create initial state for the graph
        initial_state = {
            "user_id": request.user,
            "message": request.message,
            "session_id": request.session_id or f"session_{request.user}",
            "conversation_history": [],
            "sentiment": {},
            "actions_taken": [],
            "is_final": False,
        }
        
        # Configuration for the checkpointer
        config = {
            "configurable": {
                "thread_id": request.session_id or f"thread_{request.user}",
            }
        }
        
        # Run the LangGraph workflow
        final_state = await customer_service_graph.ainvoke(initial_state, config=config)
        
        # Store conversation in background
        background_tasks.add_task(
            qdrant_service.store_conversation,
            user_id=request.user,
            message=request.message,
            response=final_state.get("response", ""),
            sentiment=final_state.get("sentiment", {}),
            session_id=final_state.get("session_id", request.session_id),
        )
        
        return ChatResponse(
            response=final_state.get("response", "I apologize, but I encountered an error processing your request."),
            sentiment=final_state.get("sentiment", {}),
            actions_taken=final_state.get("actions_taken", []),
            session_id=final_state.get("session_id", request.session_id),
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Semantic search endpoint using CLIP embeddings."""
    try:
        logger.info(f"Processing search query: {request.query}")
        
        # Generate embedding for the search query
        query_embedding = await embedding_service.get_text_embedding(request.query)
        
        # Search in Qdrant
        results = await qdrant_service.search_similar(
            query_embedding=query_embedding,
            limit=request.limit,
            include_images=request.include_images,
        )
        
        return SearchResponse(
            results=results,
            total_count=len(results),
        )
        
    except Exception as e:
        logger.error(f"Error processing search request: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Stripe webhooks."""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # Verify webhook signature
        event = stripe_service.verify_webhook(payload, sig_header)
        
        logger.info(f"Received Stripe webhook: {event['type']}")
        
        # Process webhook in background
        background_tasks.add_task(stripe_service.process_webhook_event, event)
        
        return {"status": "success"}
        
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@app.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str, limit: int = 50):
    """Get conversation history for a user."""
    try:
        conversations = await qdrant_service.get_user_conversations(user_id, limit)
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error fetching conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@app.get("/analytics/sentiment")
async def get_sentiment_analytics(days: int = 7):
    """Get sentiment analytics for the dashboard."""
    try:
        analytics = await qdrant_service.get_sentiment_analytics(days)
        return analytics
    except Exception as e:
        logger.error(f"Error fetching sentiment analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")


@app.get("/stripe/events")
async def get_stripe_events(limit: int = 50):
    """Get recent Stripe events for the dashboard."""
    try:
        events = await stripe_service.get_recent_events(limit)
        return {"events": events}
    except Exception as e:
        logger.error(f"Error fetching Stripe events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Stripe events")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
