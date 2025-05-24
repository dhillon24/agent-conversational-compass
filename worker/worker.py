
import asyncio
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Customer Service Worker",
    description="Async task processor for customer service workflow",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Customer Service Worker", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "worker": "ready"}


@app.post("/process")
async def process_task(task: TaskRequest):
    """Process a task asynchronously."""
    try:
        logger.info(f"Processing task: {task.task_type}")
        
        if task.task_type == "webhook_processing":
            result = await process_webhook_task(task.payload)
        elif task.task_type == "conversation_analysis":
            result = await process_conversation_analysis(task.payload)
        elif task.task_type == "payment_processing":
            result = await process_payment_task(task.payload)
        else:
            logger.warning(f"Unknown task type: {task.task_type}")
            result = {"status": "unknown_task_type"}
        
        logger.info(f"Task {task.task_type} completed successfully")
        return {"status": "completed", "result": result}
        
    except Exception as e:
        logger.error(f"Error processing task {task.task_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Task processing failed: {str(e)}")


async def process_webhook_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process webhook-related tasks."""
    source = payload.get("source")
    event_type = payload.get("event_type")
    data = payload.get("data", {})
    
    logger.info(f"Processing webhook from {source}: {event_type}")
    
    if source == "stripe":
        return await process_stripe_webhook(event_type, data)
    elif source == "customer_portal":
        return await process_customer_portal_webhook(event_type, data)
    else:
        return {"status": "webhook_processed", "source": source}


async def process_stripe_webhook(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process Stripe webhook events."""
    try:
        if event_type == "payment_intent.succeeded":
            # Handle successful payment
            payment_intent_id = data.get("id")
            logger.info(f"Payment succeeded: {payment_intent_id}")
            
            # Here you would typically:
            # 1. Update order status in database
            # 2. Send confirmation email
            # 3. Trigger fulfillment process
            
            return {"status": "payment_processed", "payment_id": payment_intent_id}
            
        elif event_type == "payment_intent.payment_failed":
            # Handle failed payment
            payment_intent_id = data.get("id")
            logger.info(f"Payment failed: {payment_intent_id}")
            
            return {"status": "payment_failed", "payment_id": payment_intent_id}
            
        else:
            return {"status": "stripe_event_processed", "event_type": event_type}
            
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise


async def process_customer_portal_webhook(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process customer portal webhook events."""
    logger.info(f"Processing customer portal event: {event_type}")
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    return {"status": "portal_event_processed", "event_type": event_type}


async def process_conversation_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process conversation analysis tasks."""
    user_id = payload.get("user_id")
    conversation_data = payload.get("conversation_data", {})
    
    logger.info(f"Analyzing conversation for user: {user_id}")
    
    # Simulate analysis processing
    await asyncio.sleep(0.5)
    
    # This would typically involve:
    # 1. Sentiment analysis
    # 2. Intent classification
    # 3. Entity extraction
    # 4. Response generation
    
    return {
        "status": "analysis_completed",
        "user_id": user_id,
        "sentiment": {"positive": 0.7, "neutral": 0.2, "negative": 0.1},
        "intent": "payment_inquiry",
        "entities": ["invoice_number", "payment_method"],
    }


async def process_payment_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment-related tasks."""
    user_id = payload.get("user_id")
    amount = payload.get("amount")
    currency = payload.get("currency", "usd")
    
    logger.info(f"Processing payment for user {user_id}: {amount} {currency}")
    
    # Simulate payment processing
    await asyncio.sleep(0.3)
    
    # This would typically involve:
    # 1. Validate payment details
    # 2. Create payment intent
    # 3. Process payment
    # 4. Update records
    
    return {
        "status": "payment_processed",
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
        "transaction_id": f"txn_{user_id}_{amount}",
    }


async def background_worker():
    """Background worker for periodic tasks."""
    while True:
        try:
            # Perform periodic maintenance tasks
            logger.info("Running background maintenance...")
            
            # Example tasks:
            # - Clean up old conversation data
            # - Update analytics
            # - Health checks
            
            await asyncio.sleep(300)  # Run every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in background worker: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts."""
    logger.info("Starting background worker...")
    asyncio.create_task(background_worker())


if __name__ == "__main__":
    uvicorn.run(
        "worker:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
