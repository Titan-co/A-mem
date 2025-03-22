#!/usr/bin/env python
"""
Simple direct test of ChromaDB with custom configuration
"""
# Import cache config before anything else
import cache_config

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_test")

# Print all environment variables for debugging
logger.info("Current environment variables:")
for key, value in os.environ.items():
    if "CACHE" in key or "HOME" in key or "DIR" in key or "TMP" in key:
        logger.info(f"{key}: {value}")

try:
    # Import ChromaDB
    logger.info("Importing chromadb...")
    import chromadb
    logger.info("ChromaDB imported successfully")
    
    # Create a client
    logger.info("Creating in-memory client...")
    client = chromadb.Client()
    logger.info("Client created successfully")
    
    # Create a custom embedding function
    logger.info("Creating custom embedding function...")
    from sentence_transformers import SentenceTransformer
    
    # Define a simple embedding function
    class SimpleEmbedding:
        def __init__(self):
            self.dimension = 384
            # Try to create a real model
            try:
                logger.info("Loading sentence transformer model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Model loaded successfully")
                self.use_model = True
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                logger.info("Using fallback embedding function")
                self.use_model = False
        
        def __call__(self, texts):
            if not texts:
                return []
                
            # Simple fallback if model fails
            if not self.use_model:
                return [[0.1] * self.dimension for _ in texts]
                
            # Use the real model
            try:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error during embedding: {e}")
                return [[0.1] * self.dimension for _ in texts]
    
    embedding_func = SimpleEmbedding()
    logger.info("Embedding function created successfully")
    
    # Create a collection
    logger.info("Creating collection...")
    collection = client.create_collection(
        name="test_simple",
        embedding_function=embedding_func
    )
    logger.info("Collection created successfully")
    
    # Add a document
    logger.info("Adding document...")
    collection.add(
        documents=["This is a simple test document"],
        metadatas=[{"source": "simple_test"}],
        ids=["simple-1"]
    )
    logger.info("Document added successfully")
    
    # Query
    logger.info("Querying collection...")
    results = collection.query(
        query_texts=["simple test"],
        n_results=1
    )
    logger.info(f"Query results: {results}")
    
    logger.info("SUCCESS: All ChromaDB operations completed successfully!")
    sys.exit(0)
    
except Exception as e:
    logger.error(f"ERROR: Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
