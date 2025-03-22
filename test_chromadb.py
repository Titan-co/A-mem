#!/usr/bin/env python
"""
Test script for ChromaDB functionality
This script tests if ChromaDB is properly initialized with our cache setup
"""
import os
import sys
import logging
import time
import shutil
from initialize_cache import initialize_cache, test_cache_access

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chromadb_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chromadb_test")

def test_chromadb_initialization():
    """Test if ChromaDB can be initialized properly"""
    logger.info("Testing ChromaDB initialization...")
    
    try:
        import chromadb
        from retrievers import ChromaRetriever, CACHE_DIR
        
        # First verify cache dirs
        if not test_cache_access():
            logger.error("Cache directories not properly accessible")
            return False
            
        # Test basic ChromaDB client
        try:
            logger.info("Testing basic ChromaDB client...")
            client = chromadb.Client()
            logger.info("[OK] Basic ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"BAD Failed to initialize basic ChromaDB client: {e}")
            return False
            
        # Test persistent client with our cache dir
        persist_dir = os.path.join(CACHE_DIR, "chromadb_data")
        try:
            logger.info(f"Testing ChromaDB PersistentClient with path: {persist_dir}")
            client = chromadb.PersistentClient(path=persist_dir)
            logger.info("[OK] ChromaDB PersistentClient initialized successfully")
        except Exception as e:
            logger.warning(f"BAD Failed to initialize ChromaDB PersistentClient: {e}")
            logger.info("This is not a critical failure, testing our ChromaRetriever...")
        
        # Test our ChromaRetriever class
        logger.info("Testing ChromaRetriever class...")
        retriever = ChromaRetriever(collection_name="test_collection")
        
        if retriever.client is None or retriever.collection is None:
            logger.error("[ERROR] ChromaRetriever failed to initialize properly")
            return False
            
        logger.info("[OK] ChromaRetriever initialized successfully")
        
        # Test adding a document
        logger.info("Testing document addition...")
        test_doc = "This is a test document for ChromaDB"
        test_metadata = {"tag": "test", "category": "testing"}
        test_id = "test-1"
        
        success = retriever.add_document(
            document=test_doc,
            metadata=test_metadata,
            doc_id=test_id
        )
        
        if not success:
            logger.error("[ERROR] Failed to add document to ChromaDB")
            return False
            
        logger.info("[OK] Document added successfully")
        
        # Test searching
        logger.info("Testing search functionality...")
        results = retriever.search("test document", k=1)
        
        if not results or 'ids' not in results or not results['ids'] or not results['ids'][0]:
            logger.error("[ERROR] Search returned no results")
            return False
            
        if test_id not in results['ids'][0]:
            logger.error(f"[ERROR] Search did not return expected document ID. Got: {results['ids'][0]}")
            return False
            
        logger.info("[OK] Search returned expected results")
        
        # Test deletion
        logger.info("Testing document deletion...")
        success = retriever.delete_document(test_id)
        
        if not success:
            logger.error("[ERROR] Failed to delete document from ChromaDB")
            return False
            
        logger.info("[OK] Document deleted successfully")
        
        # All tests passed!
        logger.info("All ChromaDB tests passed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required packages are installed")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during ChromaDB testing: {e}")
        return False

def test_full_memory_system():
    """Test the full memory system with ChromaDB enabled"""
    logger.info("Testing full memory system with ChromaDB enabled...")
    
    try:
        from memory_system import AgenticMemorySystem
        
        # Make sure DISABLE_CHROMADB is not set
        if "DISABLE_CHROMADB" in os.environ:
            del os.environ["DISABLE_CHROMADB"]
        
        # Initialize the memory system
        logger.info("Initializing AgenticMemorySystem...")
        memory_system = AgenticMemorySystem(
            model_name='all-MiniLM-L6-v2',
            llm_backend="openai",
            llm_model="gpt-4"
        )
        
        # Check if retrievers were properly initialized
        if memory_system.retriever is None or memory_system.chroma_retriever is None:
            logger.error("[ERROR] Retrievers were not properly initialized")
            return False
            
        logger.info("[OK] Memory system initialized with retrievers")
        
        # Create a test memory
        logger.info("Creating test memory...")
        try:
            # Disable LLM for testing to avoid API calls
            os.environ["DISABLE_LLM"] = "true"
            
            test_content = "ChromaDB test memory content"
            memory_id = memory_system.create(
                content=test_content,
                tags=["chromadb", "test"],
                category="Testing"
            )
            
            logger.info(f"[OK] Memory created with ID: {memory_id}")
            
            # Get the memory back
            memory = memory_system.read(memory_id)
            if memory is None or memory.content != test_content:
                logger.error("[ERROR] Memory retrieval failed")
                return False
                
            logger.info("[OK] Memory retrieved successfully")
            
            # Search for the memory
            results = memory_system.search("chromadb test", k=5)
            
            if not results:
                logger.error("[ERROR] Search returned no results")
                return False
                
            found = False
            for result in results:
                if result.get('id') == memory_id:
                    found = True
                    break
                    
            if not found:
                logger.error("[ERROR] Search did not return the created memory")
                return False
                
            logger.info("[OK] Search found the created memory")
            
            # Delete the memory
            success = memory_system.delete(memory_id)
            if not success:
                logger.error("[ERROR] Memory deletion failed")
                return False
                
            logger.info("[OK] Memory deleted successfully")
            
            # All tests passed!
            logger.info("All memory system tests passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during memory system test: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in memory system test: {e}")
        return False

if __name__ == "__main__":
    # Check for arguments
    force_recreate = "--force" in sys.argv
    
    # Step 1: Initialize cache
    logger.info("Step 1: Initialize cache directories")
    initialize_cache(force_recreate)
    
    # Step 2: Test ChromaDB initialization
    logger.info("\nStep 2: Test ChromaDB initialization")
    chromadb_ok = test_chromadb_initialization()
    
    if not chromadb_ok:
        logger.error("ChromaDB initialization failed")
        sys.exit(1)
    
    # Step 3: Test full memory system
    logger.info("\nStep 3: Test full memory system")
    memory_system_ok = test_full_memory_system()
    
    if not memory_system_ok:
        logger.error("Full memory system test failed")
        sys.exit(1)
    
    # All tests passed!
    logger.info("\nGOOD All tests passed! ChromaDB is working properly with the cache setup.")
    sys.exit(0)
