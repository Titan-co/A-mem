"""
Custom embedding function for ChromaDB that uses local cache directories
"""
import os
import sys
import logging
import tempfile
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Get the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, ".cache")

# Model names
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Ensure cache directories exist
os.makedirs(os.path.join(CACHE_DIR, "sentence_transformers"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "transformers"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "tmp"), exist_ok=True)

class LocalCacheEmbeddingFunction:
    """Custom embedding function that uses local cache"""
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
        normalize_embeddings: bool = True
    ):
        """Initialize with model from local cache
        
        Args:
            model_name: Name of the model to load
            device: Device to run model on (cpu/cuda)
            normalize_embeddings: Whether to normalize embeddings
        """
        # Set environment variables before importing any models
        os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(CACHE_DIR, "sentence_transformers")
        os.environ["TRANSFORMERS_CACHE"] = os.path.join(CACHE_DIR, "transformers")
        os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "transformers")
        os.environ["TMPDIR"] = os.path.join(CACHE_DIR, "tmp")
        
        # Temporary directory that will be cleaned up when the function is done
        self.temp_dir = None
        
        # Initialize model
        try:
            logger.info(f"Loading sentence transformer model from local cache: {model_name}")
            self.model = SentenceTransformer(model_name, device=device)
            self.normalize = normalize_embeddings
            logger.info(f"Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Will use fallback embedding function")
            self.model = None
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for the given texts
        
        Args:
            input: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not input:
            return []
        
        # Use model if available
        if self.model:
            try:
                # Create embeddings
                embeddings = self.model.encode(input, normalize_embeddings=self.normalize)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                # Fall back to simple embedding if model fails
        
        # Simple fallback embedding if model isn't available or fails
        logger.warning("Using fallback embedding function")
        embeddings = []
        for text in input:
            # Simple checksum-based embedding (not semantic but provides consistent vectors)
            embedding = [0.0] * 384  # Match dimension of the default model
            for i, char in enumerate(text):
                # Use character values to create a simple embedding
                pos = i % 384
                embedding[pos] += ord(char) / 255.0
            
            # Normalize the embedding
            import numpy as np
            embedding = np.array(embedding)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            embeddings.append(embedding.tolist())
            
        return embeddings
