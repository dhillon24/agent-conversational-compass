
import logging
import os
from typing import Dict, Any, List

import stripe
from stripe.error import StripeError

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        self.api_key = os.getenv("STRIPE_API_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if self.api_key:
            stripe.api_key = self.api_key
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Create a Stripe payment intent."""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )
            
            logger.info(f"Created payment intent: {payment_intent.id}")
            
            return {
                "id": payment_intent.id,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret,
            }
            
        except StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    async def create_checkout_session(
        self,
        price_data: Dict[str, Any],
        success_url: str,
        cancel_url: str,
        metadata: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session."""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": price_data,
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            
            logger.info(f"Created checkout session: {checkout_session.id}")
            
            return {
                "id": checkout_session.id,
                "url": checkout_session.url,
            }
            
        except StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    def verify_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Verify Stripe webhook signature."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise
    
    async def process_webhook_event(self, event: Dict[str, Any]):
        """Process a Stripe webhook event."""
        event_type = event["type"]
        
        try:
            if event_type == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                logger.info(f"Payment succeeded: {payment_intent['id']}")
                # Handle successful payment
                
            elif event_type == "payment_intent.payment_failed":
                payment_intent = event["data"]["object"]
                logger.info(f"Payment failed: {payment_intent['id']}")
                # Handle failed payment
                
            elif event_type == "checkout.session.completed":
                session = event["data"]["object"]
                logger.info(f"Checkout session completed: {session['id']}")
                # Handle completed checkout
                
            else:
                logger.info(f"Unhandled event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error processing webhook event {event_type}: {e}")
            raise
    
    async def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent Stripe events for the dashboard."""
        try:
            events = stripe.Event.list(limit=limit)
            
            formatted_events = []
            for event in events.data:
                formatted_events.append({
                    "id": event.id,
                    "type": event.type,
                    "created": event.created,
                    "data": event.data.object,
                })
            
            return formatted_events
            
        except StripeError as e:
            logger.error(f"Error fetching Stripe events: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Stripe events: {e}")
            return []
