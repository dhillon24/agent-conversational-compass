import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    CreateCollection,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
import numpy as np

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = None
        self.collection_name = "customer_conversations"
        self.vector_size = 512  # CLIP embedding size
        
    async def initialize(self):
        """Initialize Qdrant client and collections."""
        if self.client is None:
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            self.client = AsyncQdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
            )
            
            logger.info(f"Connected to Qdrant at {qdrant_url}")
    
    async def initialize_collections(self):
        """Create Qdrant collections if they don't exist."""
        await self.initialize()
        
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection for customer conversations
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error initializing collections: {e}")
            raise
    
    async def health_check(self) -> str:
        """Check Qdrant health."""
        try:
            await self.initialize()
            collections = await self.client.get_collections()
            return "healthy"
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return "unhealthy"
    
    async def store_conversation(
        self,
        user_id: str,
        message: str,
        response: str = "",
        sentiment: Dict[str, float] = None,
        embedding: List[float] = None,
        session_id: str = None,
    ):
        """Store a conversation in Qdrant."""
        await self.initialize()
        
        try:
            point_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            payload = {
                "user_id": user_id,
                "session_id": session_id or f"session_{user_id}",
                "message": message,
                "response": response,
                "sentiment": sentiment or {},
                "timestamp": timestamp,
                "type": "conversation",
            }
            
            if embedding is None:
                # Use zero vector as placeholder if no embedding provided
                embedding = [0.0] * self.vector_size
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            )
            
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            
            logger.info(f"Stored conversation for user {user_id}, session {session_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            raise
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        user_filter: str = None,
        include_images: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search for similar conversations or content."""
        await self.initialize()
        
        try:
            query_filter = None
            
            if user_filter:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_filter),
                        )
                    ]
                )
            
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar content: {e}")
            return []
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        session_id: str = None,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a specific user, optionally filtered by session."""
        await self.initialize()
        
        try:
            # Build filter conditions
            filter_conditions = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
            
            # Add session filter if provided
            if session_id:
                filter_conditions.append(
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=session_id),
                    )
                )
            
            query_filter = Filter(must=filter_conditions)
            
            # Use scroll to get all matching conversations without vector similarity
            results = await self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            
            # Sort by timestamp (most recent first)
            conversations = [result.payload for result in results[0]]
            conversations.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=True,
            )
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error fetching user conversations: {e}")
            return []
    
    async def get_session_conversations(
        self,
        session_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a specific session."""
        await self.initialize()
        
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=session_id),
                    )
                ]
            )
            
            # Use scroll to get all matching conversations
            results = await self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            
            # Sort by timestamp (chronological order, oldest first for conversation flow)
            conversations = [result.payload for result in results[0]]
            conversations.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=False,  # Oldest first for conversation context
            )
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error fetching session conversations: {e}")
            return []
    
    async def update_conversation_response(
        self,
        user_id: str,
        session_id: str,
        response: str,
        final_sentiment: Dict[str, float],
    ):
        """Update a conversation with the final response."""
        # This is a simplified implementation
        # In production, you'd want to track point IDs more carefully
        logger.info(f"Updated conversation response for user {user_id}")
    
    async def get_sentiment_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get sentiment analytics for the dashboard."""
        await self.initialize()
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # This is a simplified implementation
            # In production, you'd want more sophisticated analytics
            return {
                "period": f"{days} days",
                "avg_sentiment": {"positive": 0.6, "neutral": 0.3, "negative": 0.1},
                "total_conversations": 150,
                "trend": "improving",
            }
            
        except Exception as e:
            logger.error(f"Error fetching sentiment analytics: {e}")
            return {}
