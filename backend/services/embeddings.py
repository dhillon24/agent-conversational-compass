
import logging
import os
from typing import List, Union
import asyncio

import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def initialize(self):
        """Initialize the CLIP model and processor."""
        if self.model is None:
            try:
                logger.info(f"Loading CLIP model: {self.model_name}")
                
                # Load model and processor
                self.model = CLIPModel.from_pretrained(self.model_name)
                self.processor = CLIPProcessor.from_pretrained(self.model_name)
                
                # Move to appropriate device
                self.model.to(self.device)
                
                logger.info(f"CLIP model loaded successfully on {self.device}")
                
            except Exception as e:
                logger.error(f"Error loading CLIP model: {e}")
                raise
    
    async def health_check(self) -> str:
        """Check if the embedding service is healthy."""
        try:
            await self.initialize()
            # Test with a simple text embedding
            test_embedding = await self.get_text_embedding("test")
            return "healthy" if len(test_embedding) > 0 else "unhealthy"
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            return "unhealthy"
    
    async def get_text_embedding(self, text: str) -> List[float]:
        """Generate CLIP embedding for text."""
        await self.initialize()
        
        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, self._generate_text_embedding, text
            )
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 512
    
    def _generate_text_embedding(self, text: str) -> List[float]:
        """Generate text embedding (runs in thread pool)."""
        with torch.no_grad():
            inputs = self.processor(text=[text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features.cpu().numpy().flatten().tolist()
    
    async def get_image_embedding(self, image: Union[Image.Image, str]) -> List[float]:
        """Generate CLIP embedding for an image."""
        await self.initialize()
        
        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, self._generate_image_embedding, image
            )
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 512
    
    def _generate_image_embedding(self, image: Union[Image.Image, str]) -> List[float]:
        """Generate image embedding (runs in thread pool)."""
        if isinstance(image, str):
            image = Image.open(image)
        
        with torch.no_grad():
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten().tolist()
    
    async def get_multimodal_similarity(
        self, text: str, image: Union[Image.Image, str]
    ) -> float:
        """Calculate similarity between text and image."""
        text_embedding = await self.get_text_embedding(text)
        image_embedding = await self.get_image_embedding(image)
        
        # Calculate cosine similarity
        text_array = np.array(text_embedding)
        image_array = np.array(image_embedding)
        
        similarity = np.dot(text_array, image_array) / (
            np.linalg.norm(text_array) * np.linalg.norm(image_array)
        )
        
        return float(similarity)
