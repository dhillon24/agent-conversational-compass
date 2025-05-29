import logging
from typing import Dict, Any, List
import asyncio
import os
import re
from pathlib import Path

from services.qdrant_client import QdrantService
from services.embeddings import EmbeddingService
from services.stripe_client import StripeService
from services.mcp_client import mcp_client
import openai
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables from .env file in project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Initialize services
qdrant_service = QdrantService()
embedding_service = EmbeddingService()
stripe_service = StripeService()

# Initialize OpenAI client lazily
openai_client = None
sentiment_analyzer = None


async def get_openai_client():
    """Lazy initialization of OpenAI client."""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        # Check for valid OpenAI API key (should start with sk- and not be a placeholder)
        if (not api_key or 
            api_key in ["sk-your-openai-api-key-here", "sk-test-key"] or 
            not api_key.startswith("sk-") or
            api_key.startswith("sk-test") or
            len(api_key) < 20):  # Real OpenAI keys are much longer
            # Use a dummy client for development/testing
            openai_client = openai.AsyncOpenAI(api_key="dummy-key-for-testing")
        else:
            openai_client = openai.AsyncOpenAI(api_key=api_key)
    return openai_client


async def get_sentiment_analyzer():
    """Lazy initialization of sentiment analyzer."""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            return_all_scores=True,
        )
    return sentiment_analyzer


async def ingest_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest and store the interaction in Qdrant for future retrieval."""
    logger.info(f"Ingest node processing for user: {state['user_id']}")
    
    try:
        # Generate embedding for the user message
        message_embedding = await embedding_service.get_text_embedding(state["message"])
        
        # Store in Qdrant with metadata
        await qdrant_service.store_conversation(
            user_id=state["user_id"],
            message=state["message"],
            response="",  # Will be updated later
            sentiment=state.get("sentiment", {}),
            embedding=message_embedding,
            session_id=state.get("session_id"),
        )
        
        # Retrieve actual conversation history for this session
        # This gives us the chronological conversation history for the current session
        session_conversations = await qdrant_service.get_session_conversations(
            session_id=state.get("session_id", f"session_{state['user_id']}"),
            limit=10  # Get last 10 conversations in this session for context
        )
        
        # Also get recent conversations from this user (across sessions) for broader context
        user_conversations = await qdrant_service.get_user_conversations(
            user_id=state["user_id"],
            limit=5  # Get last 5 conversations from user across all sessions
        )
        
        # Also get semantically similar conversations for additional context
        similar_conversations = await qdrant_service.search_similar(
            query_embedding=message_embedding,
            limit=3,
            user_filter=state["user_id"],
        )
        
        # Prioritize session conversations, then user conversations
        state["conversation_history"] = session_conversations
        state["user_conversations"] = user_conversations
        state["similar_conversations"] = similar_conversations
        state["actions_taken"].append("stored_interaction")
        
        logger.info(f"Successfully ingested interaction for user: {state['user_id']}, session: {state.get('session_id')}, retrieved {len(session_conversations)} session conversations")
        
    except Exception as e:
        logger.error(f"Error in ingest node: {e}")
        state["actions_taken"].append(f"ingest_error: {str(e)}")
        state["conversation_history"] = []
        state["user_conversations"] = []
        state["similar_conversations"] = []
    
    return state


async def sentiment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze sentiment of the user message using RoBERTa."""
    logger.info(f"Sentiment analysis for user: {state['user_id']}")
    
    try:
        analyzer = await get_sentiment_analyzer()
        sentiment_scores = analyzer(state["message"])
        
        # Convert to a more readable format
        sentiment_dict = {}
        for score in sentiment_scores[0]:  # First (and only) result
            sentiment_dict[score["label"]] = score["score"]
        
        state["sentiment"] = sentiment_dict
        state["actions_taken"].append("sentiment_analyzed")
        
        logger.info(f"Sentiment analysis completed: {sentiment_dict}")
        
    except Exception as e:
        logger.error(f"Error in sentiment node: {e}")
        state["sentiment"] = {"error": str(e)}
        state["actions_taken"].append(f"sentiment_error: {str(e)}")
    
    return state


async def action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle business transactions and actions (e.g., Stripe payments, order lookups)."""
    logger.info(f"Action node processing for user: {state['user_id']}")
    
    message = state["message"].lower()
    
    try:
        # Initialize MCP client if needed
        if not mcp_client.client:
            await mcp_client.initialize()
        
        # Check for order-related queries
        order_keywords = ["order", "status", "tracking", "shipment", "delivery", "shipped"]
        if any(keyword in message for keyword in order_keywords):
            # Extract order number from message
            order_match = re.search(r'#?(\d+)', message)
            
            if order_match:
                order_number = order_match.group(1)
                logger.info(f"Detected order query for order #{order_number}")
                
                # Fetch order details from database via MCP
                order_result = await mcp_client.get_order_details(order_number)
                
                if order_result.get("success") and order_result.get("result", {}).get("success"):
                    order_data = order_result["result"]
                    state["order_data"] = order_data
                    state["actions_taken"].append(f"order_lookup_success: {order_number}")
                    logger.info(f"Successfully retrieved order data for #{order_number}")
                else:
                    error_msg = order_result.get("result", {}).get("error", "Unknown error")
                    state["order_lookup_error"] = error_msg
                    state["actions_taken"].append(f"order_lookup_failed: {order_number} - {error_msg}")
                    logger.warning(f"Order lookup failed for #{order_number}: {error_msg}")
            else:
                # Check if user is asking about "my order" or similar without specific number
                if any(phrase in message for phrase in ["my order", "my orders", "order status"]):
                    state["actions_taken"].append("order_query_without_number")
                    logger.info("User asking about orders but no order number provided")
        
        # Check for order history queries (e.g., "show me order history for customer123")
        history_keywords = ["history", "orders", "past orders", "previous orders", "order list"]
        if any(keyword in message for keyword in history_keywords):
            # Look for customer identifier in the message
            customer_patterns = [
                r'customer(\d+)',  # customer123, customer1, etc.
                r'customer\s+(\d+)',  # customer 123, customer 1, etc.
                r'for\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',  # email addresses
                r'user\s+id[:\s]+([a-zA-Z0-9-]+)',  # user id: xxx
            ]
            
            customer_identifier = None
            for pattern in customer_patterns:
                match = re.search(pattern, message)
                if match:
                    if '@' in match.group(1):
                        customer_identifier = match.group(1)  # email
                    else:
                        customer_identifier = f"customer{match.group(1)}"  # customer123 format
                    break
            
            # Authorization check: Ensure user can only access their own data
            requesting_user = state.get("user_id", "").lower()
            
            # Define authorized roles that can access any customer's data
            authorized_agent_users = [
                "customer_service_agent",
                "support_agent", 
                "admin",
                "cs_agent",
                "agent"
            ]
            
            is_authorized_agent = any(role in requesting_user for role in authorized_agent_users)
            
            if customer_identifier:
                # Check if user is requesting their own data or if they're an authorized agent
                is_own_data = False
                
                if customer_identifier == requesting_user:
                    is_own_data = True
                elif customer_identifier.startswith("customer") and customer_identifier.replace("customer", "") in requesting_user:
                    is_own_data = True
                elif "@" in customer_identifier and customer_identifier == requesting_user:
                    is_own_data = True
                
                # Allow access only if it's own data or user is an authorized agent
                if is_own_data or is_authorized_agent:
                    logger.info(f"Authorized order history request for customer: {customer_identifier} by user: {requesting_user}")
                    
                    # First, get customer info to validate and get details
                    customer_result = await mcp_client.get_customer_by_identifier(customer_identifier)
                    
                    if customer_result.get("success") and customer_result.get("result", {}).get("success"):
                        customer_info = customer_result["result"]["customer"]
                        
                        # Now get order history for this customer
                        orders_result = await mcp_client.get_customer_orders(customer_info["email"], limit=10)
                        
                        if orders_result.get("success") and orders_result.get("result", {}).get("success"):
                            state["customer_order_history"] = {
                                "customer": customer_info,
                                "orders": orders_result["result"]["orders"],
                                "total_orders": orders_result["result"]["total_orders"]
                            }
                            state["actions_taken"].append(f"order_history_retrieved: {customer_identifier}")
                            logger.info(f"Successfully retrieved order history for {customer_identifier}: {len(orders_result['result']['orders'])} orders")
                        else:
                            error_msg = orders_result.get("result", {}).get("error", "Unknown error")
                            state["order_history_error"] = error_msg
                            state["actions_taken"].append(f"order_history_failed: {customer_identifier} - {error_msg}")
                            logger.warning(f"Order history lookup failed for {customer_identifier}: {error_msg}")
                    else:
                        error_msg = customer_result.get("result", {}).get("error", "Customer not found")
                        state["customer_lookup_error"] = error_msg
                        state["actions_taken"].append(f"customer_lookup_failed: {customer_identifier} - {error_msg}")
                        logger.warning(f"Customer lookup failed for {customer_identifier}: {error_msg}")
                else:
                    # Unauthorized access attempt
                    state["unauthorized_access_attempt"] = {
                        "requested_customer": customer_identifier,
                        "requesting_user": requesting_user,
                        "reason": "User attempted to access another customer's order history"
                    }
                    state["actions_taken"].append(f"unauthorized_access_blocked: {requesting_user} tried to access {customer_identifier}")
                    logger.warning(f"SECURITY: Unauthorized access attempt - User {requesting_user} tried to access order history for {customer_identifier}")
            else:
                # Generic order history request without specific customer
                # For non-agents, assume they want their own order history
                if not is_authorized_agent:
                    customer_identifier = requesting_user
                    logger.info(f"User {requesting_user} requesting their own order history")
                    
                    # Get customer info for the requesting user
                    customer_result = await mcp_client.get_customer_by_identifier(customer_identifier)
                    
                    if customer_result.get("success") and customer_result.get("result", {}).get("success"):
                        customer_info = customer_result["result"]["customer"]
                        
                        # Get order history for this customer
                        orders_result = await mcp_client.get_customer_orders(customer_info["email"], limit=10)
                        
                        if orders_result.get("success") and orders_result.get("result", {}).get("success"):
                            state["customer_order_history"] = {
                                "customer": customer_info,
                                "orders": orders_result["result"]["orders"],
                                "total_orders": orders_result["result"]["total_orders"]
                            }
                            state["actions_taken"].append(f"own_order_history_retrieved: {customer_identifier}")
                            logger.info(f"Successfully retrieved own order history for {customer_identifier}")
                        else:
                            state["actions_taken"].append("order_history_query_no_orders_found")
                            logger.info(f"No order history found for user {requesting_user}")
                    else:
                        state["actions_taken"].append("order_history_query_user_not_found")
                        logger.info(f"User {requesting_user} not found in customer database")
                else:
                    state["actions_taken"].append("order_history_query_without_customer")
                    logger.info("Agent asking about order history but no customer identifier found")
        
        # Check if the message contains payment-related keywords
        payment_keywords = ["pay", "payment", "invoice", "bill", "charge", "transaction"]
        
        if any(keyword in message for keyword in payment_keywords):
            # Extract potential invoice/bill number
            invoice_match = re.search(r'#?(\d+)', message)
            
            if invoice_match:
                invoice_number = invoice_match.group(1)
                
                # Create a test Stripe payment intent
                payment_result = await stripe_service.create_payment_intent(
                    amount=1000,  # $10.00 in cents
                    currency="usd",
                    metadata={
                        "user_id": state["user_id"],
                        "invoice_number": invoice_number,
                        "session_id": state["session_id"],
                    },
                )
                
                state["payment_intent"] = payment_result
                state["actions_taken"].append(f"payment_intent_created: {payment_result['id']}")
                
                logger.info(f"Payment intent created: {payment_result['id']}")
            else:
                state["actions_taken"].append("payment_requested_but_no_invoice_found")
        
        # Check for customer information queries
        customer_keywords = ["customer", "account", "profile", "information"]
        if any(keyword in message for keyword in customer_keywords):
            # Try to get customer info if we have an email
            user_id = state.get("user_id")
            if user_id and "@" in user_id:  # Assuming user_id might be email
                customer_result = await mcp_client.get_customer_info(user_id)
                if customer_result.get("success") and customer_result.get("result", {}).get("success"):
                    state["customer_data"] = customer_result["result"]
                    state["actions_taken"].append("customer_info_retrieved")
        
        # Check for other action keywords
        if "cancel" in message and "subscription" in message:
            state["actions_taken"].append("subscription_cancellation_requested")
        
        if "refund" in message:
            state["actions_taken"].append("refund_requested")
            
    except Exception as e:
        logger.error(f"Error in action node: {e}")
        state["actions_taken"].append(f"action_error: {str(e)}")
    
    return state


async def policy_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Apply business policies and generate response using OpenAI ChatGPT o1."""
    logger.info(f"Policy node processing for user: {state['user_id']}")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"API key check: key='{api_key}', length={len(api_key) if api_key else 0}, starts_with_sk_test={api_key.startswith('sk-test') if api_key else False}")
        
        # Check if we have a valid OpenAI API key (should start with sk- and not be a placeholder)
        if (not api_key or 
            api_key in ["sk-your-openai-api-key-here", "sk-test-key"] or 
            not api_key.startswith("sk-") or
            api_key.startswith("sk-test") or
            len(api_key) < 20):  # Real OpenAI keys are much longer
            # Provide a fallback response when no valid API key is available
            logger.info("No valid OpenAI API key found, using fallback response")
            
            # Generate a simple rule-based response
            message = state["message"].lower()
            sentiment = state.get("sentiment", {})
            actions = state.get("actions_taken", [])
            
            # Check for order-related responses with real data
            order_data = state.get("order_data")
            if order_data and any("order_lookup_success" in action for action in actions):
                # Use real order data to generate response
                order_info = f"I found your order #{order_data['order_number']}! Here are the details:\n\n"
                order_info += f"Status: {order_data['status']}\n"
                order_info += f"Payment Status: {order_data['payment_status']}\n"
                order_info += f"Total Amount: ${order_data['total_amount']}\n"
                order_info += f"Order Date: {order_data['created_at']}\n\n"
                
                order_info += "Items ordered:\n"
                for item in order_data['items']:
                    order_info += f"• {item['name']} (Qty: {item['quantity']}) - ${item['total_price']}\n"
                
                if order_data.get('shipment'):
                    shipment = order_data['shipment']
                    order_info += f"\nShipping Information:\n"
                    order_info += f"• Carrier: {shipment['carrier']}\n"
                    order_info += f"• Tracking Number: {shipment['tracking_number']}\n"
                    order_info += f"• Shipping Status: {shipment['status']}\n"
                    if shipment.get('estimated_delivery'):
                        order_info += f"• Estimated Delivery: {shipment['estimated_delivery']}\n"
                
                ai_response = order_info
            # Check for order history responses with real data
            elif state.get("customer_order_history") and any("order_history_retrieved" in action for action in actions):
                # Use real order history data to generate response
                history_data = state["customer_order_history"]
                customer = history_data["customer"]
                orders = history_data["orders"]
                
                history_info = f"Here's the order history for {customer['full_name']} ({customer['email']}):\n\n"
                history_info += f"Total Orders: {len(orders)}\n\n"
                
                for i, order in enumerate(orders, 1):
                    history_info += f"{i}. Order #{order['order_number']}\n"
                    history_info += f"   Date: {order['created_at'][:10]}\n"  # Just date part
                    history_info += f"   Status: {order['status']}\n"
                    history_info += f"   Amount: ${order['total_amount']}\n"
                    history_info += f"   Payment: {order['payment_status']}\n"
                    if order.get('delivered_at'):
                        history_info += f"   Delivered: {order['delivered_at'][:10]}\n"
                    elif order.get('shipped_at'):
                        history_info += f"   Shipped: {order['shipped_at'][:10]}\n"
                    history_info += "\n"
                
                ai_response = history_info
            # Check for unauthorized access attempts
            elif state.get("unauthorized_access_attempt"):
                unauthorized_info = state["unauthorized_access_attempt"]
                ai_response = "I'm sorry, but I cannot provide order history for other customers. For privacy and security reasons, you can only access your own order information. If you're a customer service agent, please use your authorized agent credentials."
            # Check for payment-related responses
            elif any("payment_intent_created" in action for action in actions):
                payment_intent = state.get("payment_intent", {})
                ai_response = f"Thank you for your payment request! I've initiated the payment process for you. Payment ID: {payment_intent.get('id', 'N/A')}. You should receive a confirmation email shortly."
            elif "refund" in message:
                ai_response = "I understand you're looking for a refund. I've noted your request and our billing team will review it within 24-48 hours. You'll receive an email update once the review is complete."
            elif "cancel" in message and "subscription" in message:
                ai_response = "I've received your subscription cancellation request. Your subscription will remain active until the end of your current billing period, and you won't be charged again after that."
            elif any(word in message for word in ["help", "support", "problem", "issue"]):
                ai_response = "I'm here to help! I've analyzed your message and our team is ready to assist you. Is there anything specific I can help you with today?"
            else:
                # Default friendly response
                ai_response = "Thank you for contacting us! I've received your message and I'm here to help. Our customer service team values your feedback and will ensure you receive the best possible assistance."
            
            # Add sentiment-based personalization
            if sentiment.get("LABEL_2", 0) > 0.7:  # Positive sentiment
                ai_response += " We're glad to hear from you!"
            elif sentiment.get("LABEL_0", 0) > 0.7:  # Negative sentiment
                ai_response += " We understand your concern and want to make this right for you."
            
        else:
            # Use OpenAI API when valid key is available
            # Prepare context from conversation history
            context_messages = []
            
            # Add system prompt
            system_prompt = """You are a helpful customer service AI assistant. You have access to:
            - Customer conversation history (chronological order)
            - Sentiment analysis of their current message
            - Any actions that have been taken (payments, etc.)
            - Real-time order data from the database when available
            
            Use the conversation history to maintain context and remember previous interactions.
            If the customer mentions something from a previous conversation (like an order number, 
            issue, or request), reference it appropriately.
            
            When you have real order data available, use it to provide accurate information.
            Never make up or hallucinate order details, shipping information, or product details.
            If you don't have specific information, be honest about it and offer to help find the information.
            
            Provide helpful, empathetic, and accurate responses. If payment actions were taken,
            confirm the details. Always maintain a professional and friendly tone."""
            
            context_messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history for context (chronological order, most recent first)
            conversation_history = state.get("conversation_history", [])
            if conversation_history:
                # Add session conversation history (chronological order for context)
                context_messages.append({"role": "system", "content": "=== Current Session Conversation History ==="})
                for conv in conversation_history:  # Already in chronological order (oldest first)
                    if conv.get("message"):
                        context_messages.append({"role": "user", "content": conv["message"]})
                    if conv.get("response") and conv["response"].strip():
                        context_messages.append({"role": "assistant", "content": conv["response"]})
            
            # Add broader user context if available
            user_conversations = state.get("user_conversations", [])
            if user_conversations and len(user_conversations) > len(conversation_history):
                context_messages.append({"role": "system", "content": "=== Recent conversations from other sessions (for context) ==="})
                # Add a few recent conversations from other sessions
                other_sessions = [conv for conv in user_conversations if conv not in conversation_history]
                for conv in other_sessions[:2]:  # Just 2 for context
                    if conv.get("message") and conv.get("response"):
                        context_messages.append({"role": "system", "content": f"Previous: User said '{conv['message']}' → Assistant replied '{conv['response'][:100]}...'"})
            
            # Add current message with context and real data
            current_context = f"""Current message: {state['message']}

Sentiment analysis: {state.get('sentiment', {})}
Actions taken in this session: {state.get('actions_taken', [])}"""
            
            # Add real order data if available
            order_data = state.get("order_data")
            if order_data:
                order_info = f"""

REAL ORDER DATA (use this accurate information):
Order #{order_data['order_number']}:
- Status: {order_data['status']}
- Payment Status: {order_data['payment_status']}
- Total Amount: ${order_data['total_amount']}
- Created: {order_data['created_at']}
- Customer: {order_data['customer']['name']} ({order_data['customer']['email']})

Items ordered:"""
                for item in order_data['items']:
                    order_info += f"\n  - {item['name']} (Qty: {item['quantity']}) - ${item['total_price']}"
                
                if order_data.get('shipment'):
                    shipment = order_data['shipment']
                    order_info += f"""

Shipping Information:
- Carrier: {shipment['carrier']}
- Tracking: {shipment['tracking_number']}
- Status: {shipment['status']}"""
                    if shipment.get('estimated_delivery'):
                        order_info += f"\n- Estimated Delivery: {shipment['estimated_delivery']}"
                
                current_context += order_info
            
            # Add order lookup error if any
            order_error = state.get("order_lookup_error")
            if order_error:
                current_context += f"\n\nOrder lookup error: {order_error}"
            
            # Add order history data if available
            order_history = state.get("customer_order_history")
            if order_history:
                customer = order_history["customer"]
                orders = order_history["orders"]
                
                history_info = f"""

CUSTOMER ORDER HISTORY (use this accurate information):
Customer: {customer['full_name']} ({customer['email']})
Total Orders: {len(orders)}

Order History:"""
                for i, order in enumerate(orders, 1):
                    history_info += f"""
{i}. Order #{order['order_number']}
   - Date: {order['created_at'][:10]}
   - Status: {order['status']}
   - Amount: ${order['total_amount']}
   - Payment: {order['payment_status']}"""
                    if order.get('delivered_at'):
                        history_info += f"\n   - Delivered: {order['delivered_at'][:10]}"
                    elif order.get('shipped_at'):
                        history_info += f"\n   - Shipped: {order['shipped_at'][:10]}"
                
                current_context += history_info
            
            # Add unauthorized access attempt information if any
            unauthorized_attempt = state.get("unauthorized_access_attempt")
            if unauthorized_attempt:
                security_info = f"""

SECURITY ALERT - UNAUTHORIZED ACCESS ATTEMPT:
Requesting User: {unauthorized_attempt['requesting_user']}
Requested Customer: {unauthorized_attempt['requested_customer']}
Reason: {unauthorized_attempt['reason']}

IMPORTANT: Deny this request and explain privacy/security policies. Only authorized agents can access other customers' data."""
                current_context += security_info
            
            # Add customer data if available
            customer_data = state.get("customer_data")
            if customer_data:
                customer_info = customer_data.get("customer", {})
                current_context += f"""

Customer Information:
- Name: {customer_info.get('first_name')} {customer_info.get('last_name')}
- Email: {customer_info.get('email')}
- Status: {customer_info.get('status')}"""
            
            # Add similar conversations context if available
            similar_conversations = state.get("similar_conversations", [])
            if similar_conversations:
                similar_context = "\n\nSimilar past conversations for reference:\n"
                for i, conv in enumerate(similar_conversations[:2]):  # Top 2 similar conversations
                    if conv.get("payload", {}).get("message") and conv.get("payload", {}).get("response"):
                        similar_context += f"- Previous: '{conv['payload']['message']}' → '{conv['payload']['response'][:100]}...'\n"
                current_context += similar_context
            
            context_messages.append({"role": "user", "content": current_context})
            
            # Generate response using OpenAI
            client = await get_openai_client()
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # Use gpt-4o-mini for better performance and higher rate limits
                messages=context_messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if payment was processed and add confirmation
            if any("payment_intent_created" in action for action in state.get("actions_taken", [])):
                payment_intent = state.get("payment_intent", {})
                ai_response += f"\n\nI've initiated a payment process for you. Payment ID: {payment_intent.get('id', 'N/A')}"
        
        state["response"] = ai_response
        state["is_final"] = True
        state["actions_taken"].append("response_generated")
        
        logger.info(f"Response generated for user: {state['user_id']}")
        
    except Exception as e:
        logger.error(f"Error in policy node: {e}")
        state["response"] = "I apologize, but I encountered an error while processing your request. Please try again or contact support."
        state["is_final"] = True
        state["actions_taken"].append(f"policy_error: {str(e)}")
    
    return state


async def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Update long-term memory with the completed interaction."""
    logger.info(f"Memory node updating for user: {state['user_id']}")
    
    try:
        # Update the stored conversation with the final response
        if state.get("response"):
            await qdrant_service.update_conversation_response(
                user_id=state["user_id"],
                session_id=state["session_id"],
                response=state["response"],
                final_sentiment=state.get("sentiment", {}),
            )
        
        state["actions_taken"].append("memory_updated")
        
        logger.info(f"Memory updated for user: {state['user_id']}")
        
    except Exception as e:
        logger.error(f"Error in memory node: {e}")
        state["actions_taken"].append(f"memory_error: {str(e)}")
    
    return state
