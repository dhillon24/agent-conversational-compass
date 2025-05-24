
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "running"


@patch('main.qdrant_service.health_check')
@patch('main.embedding_service.health_check')
def test_health_check(mock_embedding_health, mock_qdrant_health):
    """Test the health check endpoint."""
    mock_qdrant_health.return_value = "healthy"
    mock_embedding_health.return_value = "healthy"
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


@patch('main.customer_service_graph.ainvoke')
@patch('main.qdrant_service.store_conversation')
def test_chat_endpoint(mock_store_conversation, mock_graph_invoke):
    """Test the chat endpoint."""
    # Mock the graph response
    mock_graph_invoke.return_value = {
        "response": "I can help you with payment for invoice #123.",
        "sentiment": {"positive": 0.8, "neutral": 0.2, "negative": 0.0},
        "actions_taken": ["payment_intent_created"],
        "session_id": "test_session",
    }
    
    mock_store_conversation.return_value = None
    
    response = client.post(
        "/chat",
        json={
            "user": "test_user",
            "message": "I need help with payment for invoice #123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sentiment" in data
    assert "actions_taken" in data


@patch('main.embedding_service.get_text_embedding')
@patch('main.qdrant_service.search_similar')
def test_search_endpoint(mock_search_similar, mock_get_embedding):
    """Test the semantic search endpoint."""
    mock_get_embedding.return_value = [0.1] * 512  # Mock embedding
    mock_search_similar.return_value = [
        {
            "id": "test_id",
            "score": 0.95,
            "payload": {
                "message": "Test message",
                "user_id": "test_user",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    ]
    
    response = client.post(
        "/search",
        json={
            "query": "payment issues",
            "limit": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_count" in data
    assert len(data["results"]) > 0


def test_chat_endpoint_validation():
    """Test chat endpoint input validation."""
    # Missing user field
    response = client.post(
        "/chat",
        json={"message": "Hello"}
    )
    assert response.status_code == 422
    
    # Missing message field
    response = client.post(
        "/chat",
        json={"user": "test_user"}
    )
    assert response.status_code == 422


def test_search_endpoint_validation():
    """Test search endpoint input validation."""
    # Missing query field
    response = client.post(
        "/search",
        json={"limit": 5}
    )
    assert response.status_code == 422
    
    # Invalid limit type
    response = client.post(
        "/search",
        json={"query": "test", "limit": "invalid"}
    )
    assert response.status_code == 422


@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_invalid_signature(mock_construct_event):
    """Test Stripe webhook with invalid signature."""
    mock_construct_event.side_effect = ValueError("Invalid payload")
    
    response = client.post(
        "/stripe/webhook",
        data="invalid_payload",
        headers={"stripe-signature": "invalid_signature"}
    )
    
    assert response.status_code == 400


def test_stripe_webhook_missing_signature():
    """Test Stripe webhook with missing signature header."""
    response = client.post(
        "/stripe/webhook",
        data="test_payload"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "stripe-signature" in data["detail"]
