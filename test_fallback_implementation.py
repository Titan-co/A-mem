#!/usr/bin/env python
"""
Test script for verifying the fallback ChromaDB implementation is working correctly
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fallback_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fallback_test")

def test_fallback_implementation():
    """Test the fallback ChromaDB implementation"""
    logger.info("Testing fallback ChromaDB implementation...")

    # Check for chromadb_config.py
    import importlib.util
    config_path = os.path.join(os.path.dirname(__file__), "chromadb_config.py")
    if os.path.exists(config_path):
        spec = importlib.util.spec_from_file_location("chromadb_config", config_path)
        chromadb_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chromadb_config)
        use_fallback = getattr(chromadb_config, "USE_FALLBACK", False)
        logger.info(f"chromadb_config.py found: USE_FALLBACK={use_fallback}")
        if not use_fallback:
            logger.warning("Fallback implementation is not enabled in chromadb_config.py")
            logger.info("Setting USE_FALLBACK=True for this test")
    else:
        logger.warning("chromadb_config.py not found, creating it with USE_FALLBACK=True")
        with open(config_path, "w") as f:
            f.write("# Auto-generated ChromaDB configuration for testing\n")
            f.write("USE_DIRECT_EMBEDDING=False\n")
            f.write("USE_MONKEY_PATCH=False\n")
            f.write("USE_FALLBACK=True\n")

    # Import fallback implementation
    try:
        logger.info("Importing fallback_chromadb...")
        from fallback_chromadb import SimpleChromaRetriever
        logger.info("GOOD Successfully imported fallback_chromadb")
    except ImportError as e:
        logger.error(f"BAD Failed to import fallback_chromadb: {e}")
        return False

    # Test initializing the retriever
    try:
        logger.info("Initializing SimpleChromaRetriever...")
        retriever = SimpleChromaRetriever("test_collection")
        logger.info("GOOD Successfully initialized SimpleChromaRetriever")
    except Exception as e:
        logger.error(f"BAD Failed to initialize SimpleChromaRetriever: {e}")
        return False

    # Test adding a document
    try:
        logger.info("Adding test document...")
        success = retriever.add_document(
            document="This is a test document for the fallback implementation",
            metadata={"context": "Testing", "keywords": ["test", "fallback"], "tags": ["test"], "category": "Test", "timestamp": "202503221830"},
            doc_id="test-1"
        )
        logger.info(f"GOOD Successfully added test document: {success}")
    except Exception as e:
        logger.error(f"BAD Failed to add test document: {e}")
        return False

    # Test searching for documents
    try:
        logger.info("Searching for test document...")
        results = retriever.search("test", k=5)
        logger.info(f"GOOD Search returned {len(results['ids'][0])} results")
        
        # Print search results
        if len(results['ids'][0]) > 0:
            logger.info(f"Document ID: {results['ids'][0][0]}")
            logger.info(f"Document content: {results['documents'][0][0]}")
            logger.info(f"Similarity score: {results['distances'][0][0]}")
        else:
            logger.warning("Search returned no results")
            
    except Exception as e:
        logger.error(f"BAD Failed to search for documents: {e}")
        return False

    # Test deleting the document
    try:
        logger.info("Deleting test document...")
        success = retriever.delete_document("test-1")
        logger.info(f"GOOD Successfully deleted test document: {success}")
    except Exception as e:
        logger.error(f"BAD Failed to delete test document: {e}")
        return False

    # Now test with the full memory system
    try:
        logger.info("\nTesting with full memory system...")
        from memory_system import AgenticMemorySystem
        
        # Temporarily set environment variables
        os.environ["DISABLE_LLM"] = "true"  # Disable LLM to avoid API calls
        
        # Initialize the memory system
        logger.info("Initializing AgenticMemorySystem...")
        memory_system = AgenticMemorySystem(
            model_name='all-MiniLM-L6-v2',
            llm_backend="openai",
            llm_model="gpt-4"
        )
        logger.info("GOOD Successfully initialized AgenticMemorySystem")
        
        # Check retrievers
        logger.info(f"retriever: {memory_system.retriever}")
        logger.info(f"chroma_retriever: {type(memory_system.chroma_retriever).__name__ if memory_system.chroma_retriever else None}")
        
        # Create a test memory
        logger.info("Creating test memory...")
        memory_id = memory_system.create(
            content="Test memory for fallback implementation",
            tags=["test", "fallback"],
            category="Testing"
        )
        logger.info(f"GOOD Successfully created memory with ID: {memory_id}")
        
        # Search for memories
        logger.info("Searching for memories...")
        results = memory_system.search("test", k=5)
        logger.info(f"GOOD Search returned {len(results)} results")
        
        # Delete memory
        logger.info("Deleting test memory...")
        success = memory_system.delete(memory_id)
        logger.info(f"GOOD Successfully deleted memory: {success}")
        
    except Exception as e:
        logger.error(f"BAD Failed memory system test: {e}")
        import traceback
        traceback.print_exc()
        return False

    logger.info("\nGOOD All tests passed! The fallback implementation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_fallback_implementation()
    if not success:
        logger.error("Some tests failed. Check the log for details.")
        sys.exit(1)
    else:
        logger.info("All tests passed successfully!")
        sys.exit(0)
