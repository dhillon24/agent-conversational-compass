
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Server Dispatcher",
    description="Message dispatcher for customer service workflow",
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

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WORKER_URL = os.getenv("WORKER_URL", "http://localhost:8002")


class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1


class WebhookPayload(BaseModel):
    source: str
    event_type: str
    data: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MCP Server Dispatcher", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check backend connectivity
        async with httpx.AsyncClient() as client:
            backend_response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            backend_status = "healthy" if backend_response.status_code == 200 else "unhealthy"
        
        return {
            "status": "healthy",
            "services": {
                "backend": backend_status,
                "worker": "available",  # Simplified check
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/_queue")
async def queue_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Queue a task for processing by the worker."""
    try:
        logger.info(f"Queueing task: {request.task_type}")
        
        # Add task to background processing
        background_tasks.add_task(dispatch_to_worker, request)
        
        return {"status": "queued", "task_type": request.task_type}
        
    except Exception as e:
        logger.error(f"Error queueing task: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue task")


@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Handle incoming webhooks from external services."""
    try:
        logger.info(f"Received webhook from {payload.source}: {payload.event_type}")
        
        # Create task for webhook processing
        task_request = TaskRequest(
            task_type="webhook_processing",
            payload={
                "source": payload.source,
                "event_type": payload.event_type,
                "data": payload.data,
            },
            priority=2,  # Higher priority for webhooks
        )
        
        # Queue for processing
        background_tasks.add_task(dispatch_to_worker, task_request)
        
        return {"status": "received", "source": payload.source}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def dispatch_to_worker(task: TaskRequest):
    """Dispatch task to worker service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{WORKER_URL}/process",
                json=task.dict(),
                timeout=30.0,
            )
            
            if response.status_code == 200:
                logger.info(f"Task {task.task_type} dispatched successfully")
            else:
                logger.error(f"Worker returned status {response.status_code}")
                
    except httpx.RequestError as e:
        logger.error(f"Error dispatching to worker: {e}")
    except Exception as e:
        logger.error(f"Unexpected error dispatching task: {e}")


@app.post("/notify")
async def notify_backend(notification: Dict[str, Any]):
    """Send notification to backend service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/notifications",
                json=notification,
                timeout=10.0,
            )
            
            return {"status": "sent", "backend_status": response.status_code}
            
    except Exception as e:
        logger.error(f"Error notifying backend: {e}")
        raise HTTPException(status_code=500, detail="Notification failed")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "dispatcher:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
