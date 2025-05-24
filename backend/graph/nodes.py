
import logging
from typing import Dict, Any, List
import asyncio

from services.qdrant_client import QdrantService
from services.embeddings import EmbeddingService
from services.stripe_client import StripeService
import openai
from transformers import pipeline
import os

logger = logging.getLogger(__name__)

# Initialize services
qdrant_service = QdrantService()
embedding_service = EmbeddingService()
stripe_service = StripeService()

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize sentiment analysis pipeline
sentiment_analyzer = None


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
        )
        
        # Retrieve relevant conversation history
        similar_conversations = await qdrant_service.search_similar(
            query_embedding=message_embedding,
            limit=5,
            user_filter=state["user_id"],
        )
        
        state["conversation_history"] = similar_conversations
        state["actions_taken"].append("stored_interaction")
        
        logger.info(f"Successfully ingested interaction for user: {state['user_id']}")
        
    except Exception as e:
        logger.error(f"Error in ingest node: {e}")
        state["actions_taken"].append(f"ingest_error: {str(e)}")
    
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
    """Handle business transactions and actions (e.g., Stripe payments)."""
    logger.info(f"Action node processing for user: {state['user_id']}")
    
    message = state["message"].lower()
    
    try:
        # Check if the message contains payment-related keywords
        payment_keywords = ["pay", "payment", "invoice", "bill", "charge", "transaction"]
        
        if any(keyword in message for keyword in payment_keywords):
            # Extract potential invoice/bill number
            import re
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
        # Prepare context from conversation history
        context_messages = []
        
        # Add system prompt
        system_prompt = """You are a helpful customer service AI assistant. You have access to:
        - Customer conversation history
        - Sentiment analysis of their message
        - Any actions that have been taken (payments, etc.)
        
        Provide helpful, empathetic, and accurate responses. If payment actions were taken,
        confirm the details. Always maintain a professional and friendly tone."""
        
        context_messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history for context
        for conv in state.get("conversation_history", []):
            if conv.get("message"):
                context_messages.append({"role": "user", "content": conv["message"]})
            if conv.get("response"):
                context_messages.append({"role": "assistant", "content": conv["response"]})
        
        # Add current message
        current_context = f"""
        User message: {state['message']}
        Sentiment analysis: {state.get('sentiment', {})}
        Actions taken: {state.get('actions_taken', [])}
        """
        
        context_messages.append({"role": "user", "content": current_context})
        
        # Generate response using OpenAI
        response = await openai_client.chat.completions.create(
            model="gpt-4",  # Use gpt-4 as o1 might not be available in all regions
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
