"""
Database tools for customer service operations.
These tools provide access to customer, order, and support data through the MCP server.
"""

import logging
import os
import asyncio
from typing import Dict, Any, List, Optional
import asyncpg
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DatabaseTools:
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv("DATABASE_URL", "postgresql://cs_user:cs_password@postgres:5432/customer_service")
    
    async def initialize(self):
        """Initialize database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def get_order_details(self, order_number: str) -> Dict[str, Any]:
        """
        Get detailed order information including items, customer, and shipping details.
        
        Args:
            order_number: The order number to look up
            
        Returns:
            Dictionary containing order details or error message
        """
        try:
            async with self.pool.acquire() as conn:
                # Get order with customer information
                order_query = """
                    SELECT 
                        o.id, o.order_number, o.status, o.subtotal, o.tax_amount, 
                        o.shipping_amount, o.total_amount, o.payment_status,
                        o.shipping_address, o.billing_address, o.created_at, 
                        o.shipped_at, o.delivered_at, o.notes,
                        c.first_name, c.last_name, c.email, c.phone
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE o.order_number = $1
                """
                
                order_row = await conn.fetchrow(order_query, order_number)
                
                if not order_row:
                    return {
                        "success": False,
                        "error": f"Order #{order_number} not found",
                        "order_number": order_number
                    }
                
                # Get order items with product details
                items_query = """
                    SELECT 
                        oi.quantity, oi.unit_price, oi.total_price,
                        p.name, p.sku, p.description
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = $1
                """
                
                items_rows = await conn.fetch(items_query, order_row['id'])
                
                # Get shipment information
                shipment_query = """
                    SELECT tracking_number, carrier, status, shipped_at, 
                           estimated_delivery, delivered_at
                    FROM shipments
                    WHERE order_id = $1
                """
                
                shipment_row = await conn.fetchrow(shipment_query, order_row['id'])
                
                # Format the response
                order_details = {
                    "success": True,
                    "order_number": order_row['order_number'],
                    "status": order_row['status'],
                    "payment_status": order_row['payment_status'],
                    "total_amount": float(order_row['total_amount']),
                    "subtotal": float(order_row['subtotal']),
                    "tax_amount": float(order_row['tax_amount']),
                    "shipping_amount": float(order_row['shipping_amount']),
                    "created_at": order_row['created_at'].isoformat(),
                    "shipped_at": order_row['shipped_at'].isoformat() if order_row['shipped_at'] else None,
                    "delivered_at": order_row['delivered_at'].isoformat() if order_row['delivered_at'] else None,
                    "customer": {
                        "name": f"{order_row['first_name']} {order_row['last_name']}",
                        "email": order_row['email'],
                        "phone": order_row['phone']
                    },
                    "shipping_address": order_row['shipping_address'],
                    "items": [
                        {
                            "name": item['name'],
                            "sku": item['sku'],
                            "description": item['description'],
                            "quantity": item['quantity'],
                            "unit_price": float(item['unit_price']),
                            "total_price": float(item['total_price'])
                        }
                        for item in items_rows
                    ]
                }
                
                # Add shipment info if available
                if shipment_row:
                    order_details["shipment"] = {
                        "tracking_number": shipment_row['tracking_number'],
                        "carrier": shipment_row['carrier'],
                        "status": shipment_row['status'],
                        "shipped_at": shipment_row['shipped_at'].isoformat() if shipment_row['shipped_at'] else None,
                        "estimated_delivery": shipment_row['estimated_delivery'].isoformat() if shipment_row['estimated_delivery'] else None,
                        "delivered_at": shipment_row['delivered_at'].isoformat() if shipment_row['delivered_at'] else None
                    }
                
                return order_details
                
        except Exception as e:
            logger.error(f"Error getting order details for {order_number}: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "order_number": order_number
            }
    
    async def get_customer_orders(self, customer_email: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent orders for a customer by email.
        
        Args:
            customer_email: Customer's email address
            limit: Maximum number of orders to return
            
        Returns:
            Dictionary containing customer orders or error message
        """
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        o.order_number, o.status, o.total_amount, o.created_at,
                        o.shipped_at, o.delivered_at, o.payment_status
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE c.email = $1
                    ORDER BY o.created_at DESC
                    LIMIT $2
                """
                
                rows = await conn.fetch(query, customer_email, limit)
                
                if not rows:
                    return {
                        "success": False,
                        "error": f"No orders found for customer {customer_email}",
                        "customer_email": customer_email
                    }
                
                orders = [
                    {
                        "order_number": row['order_number'],
                        "status": row['status'],
                        "payment_status": row['payment_status'],
                        "total_amount": float(row['total_amount']),
                        "created_at": row['created_at'].isoformat(),
                        "shipped_at": row['shipped_at'].isoformat() if row['shipped_at'] else None,
                        "delivered_at": row['delivered_at'].isoformat() if row['delivered_at'] else None
                    }
                    for row in rows
                ]
                
                return {
                    "success": True,
                    "customer_email": customer_email,
                    "orders": orders,
                    "total_orders": len(orders)
                }
                
        except Exception as e:
            logger.error(f"Error getting customer orders for {customer_email}: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "customer_email": customer_email
            }
    
    async def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get customer information by email.
        
        Args:
            email: Customer's email address
            
        Returns:
            Dictionary containing customer details or error message
        """
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, email, first_name, last_name, phone, status, created_at
                    FROM customers
                    WHERE email = $1
                """
                
                row = await conn.fetchrow(query, email)
                
                if not row:
                    return {
                        "success": False,
                        "error": f"Customer with email {email} not found",
                        "email": email
                    }
                
                return {
                    "success": True,
                    "customer": {
                        "id": str(row['id']),
                        "email": row['email'],
                        "first_name": row['first_name'],
                        "last_name": row['last_name'],
                        "phone": row['phone'],
                        "status": row['status'],
                        "created_at": row['created_at'].isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting customer by email {email}: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "email": email
            }
    
    async def get_support_tickets(self, customer_email: str = None, order_number: str = None) -> Dict[str, Any]:
        """
        Get support tickets for a customer or order.
        
        Args:
            customer_email: Customer's email address (optional)
            order_number: Order number (optional)
            
        Returns:
            Dictionary containing support tickets or error message
        """
        try:
            async with self.pool.acquire() as conn:
                if order_number:
                    query = """
                        SELECT 
                            st.ticket_number, st.subject, st.description, st.status,
                            st.priority, st.category, st.created_at, st.resolved_at,
                            c.first_name, c.last_name, c.email,
                            o.order_number
                        FROM support_tickets st
                        JOIN customers c ON st.customer_id = c.id
                        LEFT JOIN orders o ON st.order_id = o.id
                        WHERE o.order_number = $1
                        ORDER BY st.created_at DESC
                    """
                    rows = await conn.fetch(query, order_number)
                elif customer_email:
                    query = """
                        SELECT 
                            st.ticket_number, st.subject, st.description, st.status,
                            st.priority, st.category, st.created_at, st.resolved_at,
                            c.first_name, c.last_name, c.email,
                            o.order_number
                        FROM support_tickets st
                        JOIN customers c ON st.customer_id = c.id
                        LEFT JOIN orders o ON st.order_id = o.id
                        WHERE c.email = $1
                        ORDER BY st.created_at DESC
                    """
                    rows = await conn.fetch(query, customer_email)
                else:
                    return {
                        "success": False,
                        "error": "Either customer_email or order_number must be provided"
                    }
                
                tickets = [
                    {
                        "ticket_number": row['ticket_number'],
                        "subject": row['subject'],
                        "description": row['description'],
                        "status": row['status'],
                        "priority": row['priority'],
                        "category": row['category'],
                        "created_at": row['created_at'].isoformat(),
                        "resolved_at": row['resolved_at'].isoformat() if row['resolved_at'] else None,
                        "customer_name": f"{row['first_name']} {row['last_name']}",
                        "customer_email": row['email'],
                        "order_number": row['order_number']
                    }
                    for row in rows
                ]
                
                return {
                    "success": True,
                    "tickets": tickets,
                    "total_tickets": len(tickets)
                }
                
        except Exception as e:
            logger.error(f"Error getting support tickets: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }
    
    async def search_orders(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search orders by order number, customer name, or email.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results or error message
        """
        try:
            async with self.pool.acquire() as conn:
                search_query = """
                    SELECT 
                        o.order_number, o.status, o.total_amount, o.created_at,
                        c.first_name, c.last_name, c.email
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE 
                        o.order_number ILIKE $1 OR
                        c.first_name ILIKE $1 OR
                        c.last_name ILIKE $1 OR
                        c.email ILIKE $1 OR
                        CONCAT(c.first_name, ' ', c.last_name) ILIKE $1
                    ORDER BY o.created_at DESC
                    LIMIT $2
                """
                
                search_pattern = f"%{query}%"
                rows = await conn.fetch(search_query, search_pattern, limit)
                
                results = [
                    {
                        "order_number": row['order_number'],
                        "status": row['status'],
                        "total_amount": float(row['total_amount']),
                        "created_at": row['created_at'].isoformat(),
                        "customer_name": f"{row['first_name']} {row['last_name']}",
                        "customer_email": row['email']
                    }
                    for row in rows
                ]
                
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "total_results": len(results)
                }
                
        except Exception as e:
            logger.error(f"Error searching orders with query '{query}': {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "query": query
            }


# Global database tools instance
db_tools = DatabaseTools() 