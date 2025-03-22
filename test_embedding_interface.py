#!/usr/bin/env python
"""
Test script to verify that our embedding functions match ChromaDB's expected interface
"""
import os
import sys
import logging
from typing import List
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("embedding_test")

def test_custom_embedding_function():
    """Test that our custom embedding function matches ChromaDB's expected interface"""
    logger.info("Testing custom embedding function...")
    
    try:
        # Import ChromaDB
        import chromadb
        # Import our custom embedding function
        from custom_embedding import LocalCacheEmbeddingFunction
        
        # Create embedding function
        ef = LocalCacheEmbeddingFunction()
        
        # Create test documents
        test_docs = ["This is a test document", "Another test document"]
        
        # Try to get embeddings
        logger.info("Calling embedding function...")
        embeddings = ef(test_docs)
        
        # Check results
        logger.info(f"Got embeddings with dimensions: {len(embeddings)}x{len(embeddings[0]) if embeddings else 0}")
        logger.info("✓ Custom embedding function works with the new interface!")
        
        # Now try with ChromaDB
        logger.info("Testing with ChromaDB client...")
        
        # Create a client
        client = chromadb.Client()
        
        # Try to create a collection with our embedding function
        logger.info("Creating collection with custom embedding function...")
        collection = client.create_collection(
            name="test_interface",
            embedding_function=ef
        )
        
        # Add documents
        logger.info("Adding documents to collection...")
        collection.add(
            documents=test_docs,
            ids=["doc1", "doc2"]
        )
        
        # Query
        logger.info("Querying collection...")
        results = collection.query(
            query_texts=["test"],
            n_results=2
        )
        
        logger.info(f"Query returned {len(results['documents'][0])} results")
        logger.info("✓ ChromaDB successfully used our custom embedding function!")
        
        return True
    except Exception as e:
        logger.error(f"Error testing custom embedding function: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_embedding_function():
    """Test that our fallback embedding function matches ChromaDB's expected interface"""
    logger.info("\nTesting fallback embedding function...")
    
    try:
        # Import ChromaDB
        import chromadb
        # Import our fallback embedding function
        from fallback_chromadb import SkipEmbeddingFunction
        
        # Create embedding function
        ef = SkipEmbeddingFunction()
        
        # Create test documents
        test_docs = ["This is a test document", "Another test document"]
        
        # Try to get embeddings
        logger.info("Calling embedding function...")
        embeddings = ef(test_docs)
        
        # Check results
        logger.info(f"Got embeddings with dimensions: {len(embeddings)}x{len(embeddings[0]) if embeddings else 0}")
        logger.info("✓ Fallback embedding function works with the new interface!")
        
        # Now try with ChromaDB
        logger.info("Testing with ChromaDB client...")
        
        # Create a client
        client = chromadb.Client()
        
        # Try to create a collection with our embedding function
        logger.info("Creating collection with fallback embedding function...")
        collection = client.create_collection(
            name="test_fallback",
            embedding_function=ef
        )
        
        # Add documents
        logger.info("Adding documents to collection...")
        collection.add(
            documents=test_docs,
            ids=["doc1", "doc2"]
        )
        
        # Query
        logger.info("Querying collection...")
        results = collection.query(
            query_texts=["test"],
            n_results=2
        )
        
        logger.info(f"Query returned {len(results['documents'][0])} results")
        logger.info("✓ ChromaDB successfully used our fallback embedding function!")
        
        return True
    except Exception as e:
        logger.error(f"Error testing fallback embedding function: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Create a .cache directory if it doesn't exist
    os.makedirs(".cache", exist_ok=True)
    os.makedirs(".cache/chromadb_data", exist_ok=True)
    
    # Set environment variables
    os.environ["CHROMADB_CACHE_DIR"] = os.path.join(os.getcwd(), ".cache")
    
    success1 = test_custom_embedding_function()
    success2 = test_fallback_embedding_function()
    
    if success1 and success2:
        logger.info("\n✓ All tests passed! The embedding functions now match ChromaDB's expected interface.")
        sys.exit(0)
    else:
        logger.error("\n✗ Some tests failed. Check the logs for details.")
        sys.exit(1)
