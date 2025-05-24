
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import numpy as np

from services.qdrant_client import QdrantService
from services.embeddings import EmbeddingService
from services.stripe_client import StripeService


class TestQdrantService:
    """Test QdrantService functionality."""
    
    def setup_method(self):
        self.qdrant_service = QdrantService()
    
    @patch('services.qdrant_client.AsyncQdrantClient')
    async def test_initialize(self, mock_client):
        """Test Qdrant client initialization."""
        await self.qdrant_service.initialize()
        assert self.qdrant_service.client is not None
        mock_client.assert_called_once()
    
    @patch('services.qdrant_client.AsyncQdrantClient')
    async def test_health_check_healthy(self, mock_client):
        """Test Qdrant health check when healthy."""
        mock_instance = AsyncMock()
        mock_instance.get_collections.return_value = MagicMock()
        mock_client.return_value = mock_instance
        
        result = await self.qdrant_service.health_check()
        assert result == "healthy"
    
    @patch('services.qdrant_client.AsyncQdrantClient')
    async def test_health_check_unhealthy(self, mock_client):
        """Test Qdrant health check when unhealthy."""
        mock_instance = AsyncMock()
        mock_instance.get_collections.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_instance
        
        result = await self.qdrant_service.health_check()
        assert result == "unhealthy"
    
    async def test_store_conversation(self):
        """Test storing conversation in Qdrant."""
        with patch.object(self.qdrant_service, 'initialize') as mock_init, \
             patch.object(self.qdrant_service, 'client') as mock_client:
            
            mock_client.upsert = AsyncMock()
            
            result = await self.qdrant_service.store_conversation(
                user_id="test_user",
                message="Test message",
                response="Test response",
                sentiment={"positive": 0.8},
                embedding=[0.1] * 512
            )
            
            mock_client.upsert.assert_called_once()
            assert isinstance(result, str)  # Should return a UUID


class TestEmbeddingService:
    """Test EmbeddingService functionality."""
    
    def setup_method(self):
        self.embedding_service = EmbeddingService()
    
    @patch('services.embeddings.CLIPModel.from_pretrained')
    @patch('services.embeddings.CLIPProcessor.from_pretrained')
    async def test_initialize(self, mock_processor, mock_model):
        """Test embedding service initialization."""
        mock_model.return_value = MagicMock()
        mock_processor.return_value = MagicMock()
        
        await self.embedding_service.initialize()
        
        assert self.embedding_service.model is not None
        assert self.embedding_service.processor is not None
    
    async def test_health_check_healthy(self):
        """Test embedding service health check when healthy."""
        with patch.object(self.embedding_service, 'initialize') as mock_init, \
             patch.object(self.embedding_service, 'get_text_embedding') as mock_embed:
            
            mock_embed.return_value = [0.1] * 512
            
            result = await self.embedding_service.health_check()
            assert result == "healthy"
    
    async def test_health_check_unhealthy(self):
        """Test embedding service health check when unhealthy."""
        with patch.object(self.embedding_service, 'initialize') as mock_init:
            mock_init.side_effect = Exception("Model load failed")
            
            result = await self.embedding_service.health_check()
            assert result == "unhealthy"
    
    async def test_get_text_embedding(self):
        """Test text embedding generation."""
        with patch.object(self.embedding_service, 'initialize') as mock_init, \
             patch.object(self.embedding_service, '_generate_text_embedding') as mock_generate:
            
            mock_generate.return_value = [0.1] * 512
            
            result = await self.embedding_service.get_text_embedding("test text")
            
            assert len(result) == 512
            assert all(isinstance(x, float) for x in result)


class TestStripeService:
    """Test StripeService functionality."""
    
    def setup_method(self):
        self.stripe_service = StripeService()
    
    @patch('stripe.PaymentIntent.create')
    async def test_create_payment_intent(self, mock_create):
        """Test creating a Stripe payment intent."""
        mock_create.return_value = MagicMock(
            id="pi_test123",
            amount=1000,
            currency="usd",
            status="requires_payment_method",
            client_secret="pi_test123_secret"
        )
        
        result = await self.stripe_service.create_payment_intent(
            amount=1000,
            currency="usd",
            metadata={"user_id": "test_user"}
        )
        
        assert result["id"] == "pi_test123"
        assert result["amount"] == 1000
        assert result["currency"] == "usd"
        mock_create.assert_called_once()
    
    @patch('stripe.checkout.Session.create')
    async def test_create_checkout_session(self, mock_create):
        """Test creating a Stripe checkout session."""
        mock_create.return_value = MagicMock(
            id="cs_test123",
            url="https://checkout.stripe.com/session123"
        )
        
        price_data = {
            "currency": "usd",
            "product_data": {"name": "Test Product"},
            "unit_amount": 1000
        }
        
        result = await self.stripe_service.create_checkout_session(
            price_data=price_data,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert result["id"] == "cs_test123"
        assert "url" in result
        mock_create.assert_called_once()
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_valid(self, mock_construct):
        """Test webhook verification with valid signature."""
        mock_event = {"type": "payment_intent.succeeded", "data": {}}
        mock_construct.return_value = mock_event
        
        result = self.stripe_service.verify_webhook(
            payload=b"test_payload",
            sig_header="test_signature"
        )
        
        assert result == mock_event
        mock_construct.assert_called_once()
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_invalid(self, mock_construct):
        """Test webhook verification with invalid signature."""
        mock_construct.side_effect = ValueError("Invalid signature")
        
        with pytest.raises(ValueError):
            self.stripe_service.verify_webhook(
                payload=b"test_payload",
                sig_header="invalid_signature"
            )
    
    async def test_process_webhook_event_payment_succeeded(self):
        """Test processing payment succeeded webhook."""
        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "amount": 1000
                }
            }
        }
        
        # Should not raise any exceptions
        await self.stripe_service.process_webhook_event(event)
    
    @patch('stripe.Event.list')
    async def test_get_recent_events(self, mock_list):
        """Test getting recent Stripe events."""
        mock_events = MagicMock()
        mock_events.data = [
            MagicMock(
                id="evt_test123",
                type="payment_intent.succeeded",
                created=1234567890,
                data=MagicMock(object={"id": "pi_test123"})
            )
        ]
        mock_list.return_value = mock_events
        
        result = await self.stripe_service.get_recent_events(limit=10)
        
        assert len(result) == 1
        assert result[0]["id"] == "evt_test123"
        assert result[0]["type"] == "payment_intent.succeeded"
        mock_list.assert_called_once_with(limit=10)
