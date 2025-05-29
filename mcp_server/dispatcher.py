import logging
import asyncio
import json
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

from database_tools import db_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup database connections."""
    logger.info("Starting MCP Server...")
    
    # Initialize database tools
    await db_tools.initialize()
    
    logger.info("MCP Server initialized successfully")
    yield
    
    # Cleanup
    await db_tools.close()
    logger.info("MCP Server shutting down...")


app = FastAPI(
    title="MCP Server - Customer Service Tools",
    description="Model Context Protocol server providing database tools for customer service",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for requests
class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    priority: str = "medium"


class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class NotificationRequest(BaseModel):
    message: str
    recipient: str
    type: str = "info"


# MCP Tool definitions
MCP_TOOLS = {
    "get_order_details": {
        "name": "get_order_details",
        "description": "Get detailed information about a specific order including items, customer details, and shipping status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number to look up (e.g., '123', '12345')"
                }
            },
            "required": ["order_number"]
        }
    },
    "get_customer_orders": {
        "name": "get_customer_orders",
        "description": "Get recent orders for a customer by their email address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_email": {
                    "type": "string",
                    "description": "Customer's email address"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of orders to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["customer_email"]
        }
    },
    "get_customer_orders_by_id": {
        "name": "get_customer_orders_by_id",
        "description": "Get recent orders for a customer by their customer ID (UUID)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's UUID identifier"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of orders to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["customer_id"]
        }
    },
    "get_customer_by_identifier": {
        "name": "get_customer_by_identifier",
        "description": "Get customer information by various identifiers (email, customer ID, or friendly name like 'customer123')",
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": "Customer identifier - can be email, UUID, friendly name (e.g., 'customer123'), or customer name"
                }
            },
            "required": ["identifier"]
        }
    },
    "get_customer_info": {
        "name": "get_customer_info",
        "description": "Get customer information by email address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Customer's email address"
                }
            },
            "required": ["email"]
        }
    },
    "get_support_tickets": {
        "name": "get_support_tickets",
        "description": "Get support tickets for a customer or order",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_email": {
                    "type": "string",
                    "description": "Customer's email address (optional)"
                },
                "order_number": {
                    "type": "string",
                    "description": "Order number (optional)"
                }
            }
        }
    },
    "search_orders": {
        "name": "search_orders",
        "description": "Search orders by order number, customer name, or email",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (order number, customer name, or email)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MCP Server - Customer Service Tools", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "tools_available": len(MCP_TOOLS)}


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "tools": list(MCP_TOOLS.values())
    }


@app.post("/tools/call")
async def call_tool(request: ToolRequest):
    """Call a specific MCP tool."""
    tool_name = request.tool_name
    parameters = request.parameters
    
    logger.info(f"Calling tool: {tool_name} with parameters: {parameters}")
    
    try:
        if tool_name == "get_order_details":
            order_number = parameters.get("order_number")
            if not order_number:
                raise HTTPException(status_code=400, detail="order_number is required")
            
            result = await db_tools.get_order_details(order_number)
            return {"success": True, "result": result}
        
        elif tool_name == "get_customer_orders":
            customer_email = parameters.get("customer_email")
            limit = parameters.get("limit", 10)
            if not customer_email:
                raise HTTPException(status_code=400, detail="customer_email is required")
            
            result = await db_tools.get_customer_orders(customer_email, limit)
            return {"success": True, "result": result}
        
        elif tool_name == "get_customer_orders_by_id":
            customer_id = parameters.get("customer_id")
            limit = parameters.get("limit", 10)
            if not customer_id:
                raise HTTPException(status_code=400, detail="customer_id is required")
            
            result = await db_tools.get_customer_orders_by_id(customer_id, limit)
            return {"success": True, "result": result}
        
        elif tool_name == "get_customer_by_identifier":
            identifier = parameters.get("identifier")
            if not identifier:
                raise HTTPException(status_code=400, detail="identifier is required")
            
            result = await db_tools.get_customer_by_identifier(identifier)
            return {"success": True, "result": result}
        
        elif tool_name == "get_customer_info":
            email = parameters.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="email is required")
            
            result = await db_tools.get_customer_by_email(email)
            return {"success": True, "result": result}
        
        elif tool_name == "get_support_tickets":
            customer_email = parameters.get("customer_email")
            order_number = parameters.get("order_number")
            
            result = await db_tools.get_support_tickets(customer_email, order_number)
            return {"success": True, "result": result}
        
        elif tool_name == "search_orders":
            query = parameters.get("query")
            limit = parameters.get("limit", 10)
            if not query:
                raise HTTPException(status_code=400, detail="query is required")
            
            result = await db_tools.search_orders(query, limit)
            return {"success": True, "result": result}
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {"success": False, "error": str(e)}


# Legacy endpoints for backward compatibility
@app.post("/_queue")
async def queue_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Queue a task for processing."""
    logger.info(f"Queuing task: {request.task_type}")
    
    # For now, just return success - can be extended for actual task queuing
    task_id = f"task_{request.task_type}_{asyncio.get_event_loop().time()}"
    
    return {
        "task_id": task_id,
        "status": "queued",
        "task_type": request.task_type,
        "priority": request.priority
    }


@app.post("/webhook")
async def handle_webhook(payload: Dict[str, Any]):
    """Handle incoming webhooks."""
    logger.info(f"Received webhook: {payload}")
    
    # Process webhook payload
    webhook_type = payload.get("type", "unknown")
    
    return {
        "status": "received",
        "type": webhook_type,
        "processed_at": asyncio.get_event_loop().time()
    }


@app.post("/notify")
async def send_notification(request: NotificationRequest):
    """Send a notification."""
    logger.info(f"Sending notification to {request.recipient}: {request.message}")
    
    return {
        "status": "sent",
        "recipient": request.recipient,
        "type": request.type,
        "message": request.message
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "dispatcher:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
