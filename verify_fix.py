#!/usr/bin/env python
"""
Verification script for the ChromaDB disable fix
This script tests memory creation with DISABLE_CHROMADB set to true
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("verify_fix")

def test_memory_creation_without_chromadb():
    """Test memory creation with ChromaDB disabled"""
    # Set the environment variable
    os.environ["DISABLE_CHROMADB"] = "true"
    os.environ["DISABLE_LLM"] = "true"  # Also disable LLM for simpler testing
    
    logger.info("Testing memory creation with DISABLE_CHROMADB=true")
    
    try:
        # Import necessary modules
        from memory_system import AgenticMemorySystem, MemoryNote
        
        # Initialize the memory system
        memory_system = AgenticMemorySystem(
            model_name='all-MiniLM-L6-v2',
            llm_backend="openai",
            llm_model="gpt-4"
        )
        
        # Check if retrievers are None
        assert memory_system.retriever is None, "Retriever should be None with DISABLE_CHROMADB=true"
        assert memory_system.chroma_retriever is None, "ChromaRetriever should be None with DISABLE_CHROMADB=true"
        
        logger.info("GOOD Memory system initialized with retrievers set to None")
        
        # Create a memory
        test_content = "This is a test memory for verification"
        memory_id = memory_system.create(
            content=test_content,
            tags=["test", "verification"],
            category="Testing"
        )
        
        # Verify the memory was created
        assert memory_id in memory_system.memories, "Memory not found in memory store"
        
        # Read the memory
        memory = memory_system.memories[memory_id]
        assert memory.content == test_content, "Memory content doesn't match"
        
        logger.info(f"GOOD Memory created successfully with ID: {memory_id}")
        
        # Search for the memory (should return empty list)
        results = memory_system.search("test", k=5)
        assert isinstance(results, list), "Search results should be a list"
        assert len(results) == 0, "Search results should be empty with DISABLE_CHROMADB=true"
        
        logger.info("GOOD Search returns empty list as expected")
        
        return True
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_creation_without_chromadb()
    logger.info(f"Test {'passed' if success else 'failed'}")
    sys.exit(0 if success else 1)
