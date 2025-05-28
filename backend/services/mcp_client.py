"""
MCP Client for calling database tools through the MCP server.
This service provides a clean interface for the backend to access customer service data.
"""

import logging
import os
import httpx
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self):
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"MCP Client initialized with URL: {self.mcp_url}")
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("MCP Client closed")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        try:
            if not self.client:
                await self.initialize()
            
            logger.info(f"Calling MCP tool: {tool_name} with parameters: {parameters}")
            
            response = await self.client.post(
                f"{self.mcp_url}/tools/call",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MCP tool {tool_name} executed successfully")
                return result
            else:
                logger.error(f"MCP tool call failed with status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"MCP server error: {response.status_code}"
                }
                
        except httpx.RequestError as e:
            logger.error(f"Network error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def get_order_details(self, order_number: str) -> Dict[str, Any]:
        """
        Get detailed order information.
        
        Args:
            order_number: The order number to look up
            
        Returns:
            Order details or error information
        """
        return await self.call_tool("get_order_details", {"order_number": order_number})
    
    async def get_customer_orders(self, customer_email: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent orders for a customer.
        
        Args:
            customer_email: Customer's email address
            limit: Maximum number of orders to return
            
        Returns:
            Customer orders or error information
        """
        return await self.call_tool("get_customer_orders", {
            "customer_email": customer_email,
            "limit": limit
        })
    
    async def get_customer_info(self, email: str) -> Dict[str, Any]:
        """
        Get customer information by email.
        
        Args:
            email: Customer's email address
            
        Returns:
            Customer information or error information
        """
        return await self.call_tool("get_customer_info", {"email": email})
    
    async def get_support_tickets(self, customer_email: str = None, order_number: str = None) -> Dict[str, Any]:
        """
        Get support tickets for a customer or order.
        
        Args:
            customer_email: Customer's email address (optional)
            order_number: Order number (optional)
            
        Returns:
            Support tickets or error information
        """
        parameters = {}
        if customer_email:
            parameters["customer_email"] = customer_email
        if order_number:
            parameters["order_number"] = order_number
            
        return await self.call_tool("get_support_tickets", parameters)
    
    async def search_orders(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search orders by various criteria.
        
        Args:
            query: Search query (order number, customer name, or email)
            limit: Maximum number of results to return
            
        Returns:
            Search results or error information
        """
        return await self.call_tool("search_orders", {
            "query": query,
            "limit": limit
        })
    
    async def health_check(self) -> str:
        """Check MCP server health."""
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.get(f"{self.mcp_url}/health")
            if response.status_code == 200:
                return "healthy"
            else:
                return "unhealthy"
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return "unhealthy"


# Global MCP client instance
mcp_client = MCPClient() 