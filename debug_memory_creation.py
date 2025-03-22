#!/usr/bin/env python
"""
Debug script specifically for memory creation
This script isolates and tests just the memory creation functionality
to help diagnose the 500 error
"""
import sys
import os
import json
import time
import traceback
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory_creation_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("memory_debug")

def test_memory_creation_directly():
    """Test memory creation using the AgenticMemorySystem directly"""
    logger.info("Testing memory creation directly using AgenticMemorySystem...")
    
    try:
        # Import necessary components
        from memory_system import AgenticMemorySystem, MemoryNote
        from config import settings
        
        # Print settings for debugging
        logger.info(f"Settings from config:")
        logger.info(f"  MODEL_NAME: {settings.MODEL_NAME}")
        logger.info(f"  LLM_BACKEND: {settings.LLM_BACKEND}")
        logger.info(f"  LLM_MODEL: {settings.LLM_MODEL}")
        logger.info(f"  API_KEY: {'[SET]' if settings.API_KEY else '[NOT SET]'}")
        logger.info(f"  API_URL: {settings.API_URL or '[NOT SET]'}")
        
        # Initialize AgenticMemorySystem with detailed error logging
        logger.info("Initializing AgenticMemorySystem...")
        
        # Create a simple memory system with evolution disabled
        try:
            memory_system = AgenticMemorySystem(
                model_name=settings.MODEL_NAME,
                llm_backend=settings.LLM_BACKEND,
                llm_model=settings.LLM_MODEL,
                evo_threshold=settings.EVO_THRESHOLD,
                api_key=settings.API_KEY,
                api_base=settings.API_URL
            )
            
            # Disable memory evolution for testing
            def mock_evolution(note):
                logger.info("Memory evolution disabled for testing")
                return False
                
            # Replace the original method with our mock
            memory_system._process_memory_evolution = mock_evolution
            
            logger.info("✓ Memory system initialized successfully")
            
            # Step by step tests to find the issue
            
            # 1. First test the analyze_content method
            logger.info("Step 1: Testing content analysis...")
            test_content = "This is a simple test content for debugging memory creation"
            
            try:
                logger.info("Calling analyze_content...")
                analysis_result = memory_system.analyze_content(test_content)
                logger.info(f"✓ Content analysis successful: {json.dumps(analysis_result)}")
            except Exception as e:
                logger.error(f"✗ Content analysis failed: {e}")
                logger.error(traceback.format_exc())
                return False
            
            # 2. Test simple memory creation
            logger.info("\nStep 2: Testing basic memory creation...")
            try:
                logger.info("Calling memory_system.create...")
                memory_id = memory_system.create(
                    content=test_content,
                    tags=["test", "debug"],
                    category="Testing"
                )
                logger.info(f"✓ Memory created with ID: {memory_id}")
            except Exception as e:
                logger.error(f"✗ Memory creation failed: {e}")
                logger.error(traceback.format_exc())
                return False
            
            # 3. Test memory retrieval
            logger.info("\nStep 3: Testing memory retrieval...")
            try:
                logger.info(f"Retrieving memory with ID: {memory_id}")
                memory = memory_system.read(memory_id)
                if memory:
                    logger.info(f"✓ Memory retrieved successfully:")
                    logger.info(f"  ID: {memory.id}")
                    logger.info(f"  Content: {memory.content[:50]}...")
                    logger.info(f"  Tags: {memory.tags}")
                    logger.info(f"  Keywords: {memory.keywords}")
                else:
                    logger.error(f"✗ Memory not found after creation: {memory_id}")
                    return False
            except Exception as e:
                logger.error(f"✗ Memory retrieval failed: {e}")
                logger.error(traceback.format_exc())
                return False
            
            # 4. Test search functionality
            logger.info("\nStep 4: Testing search functionality...")
            try:
                logger.info("Searching for the test memory...")
                results = memory_system.search("test debug", k=5)
                logger.info(f"Found {len(results)} results")
                if results:
                    logger.info(f"✓ Search successful, first result: {results[0].get('id')} (Score: {results[0].get('score')})")
                else:
                    logger.warning("No search results found, but this might be normal for a new memory")
            except Exception as e:
                logger.error(f"✗ Search failed: {e}")
                logger.error(traceback.format_exc())
                # Don't return False here as search isn't critical for memory creation
            
            # All memory system tests passed
            logger.info("\n✓ All memory system tests passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"✗ Memory system initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to import necessary modules: {e}")
        logger.error(traceback.format_exc())
        return False

def test_memory_creation_api(port=8903):
    """Test memory creation through the API"""
    logger.info(f"Testing memory creation through API on port {port}...")
    
    try:
        import requests
        
        base_url = f"http://localhost:{port}"
        logger.info(f"API URL: {base_url}")
        
        # Check if server is running first
        try:
            logger.info("Checking if server is running (health check)...")
            response = requests.get(f"{base_url}/health", timeout=5)
            
            if response.status_code != 200:
                logger.error(f"✗ Server is not responding correctly: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            else:
                logger.info("✓ Server is running and responding to health check")
        except Exception as e:
            logger.error(f"✗ Server is not running or not accessible: {e}")
            return False
        
        # Test memory creation with verbose logging
        logger.info("\nTesting memory creation API...")
        test_content = f"Memory created during API test at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            logger.info(f"Sending POST request to {base_url}/api/v1/memories")
            logger.info(f"Request data: {json.dumps({'content': test_content, 'tags': ['api', 'test']})}")
            
            # Set a long timeout
            response = requests.post(
                f"{base_url}/api/v1/memories",
                json={"content": test_content, "tags": ["api", "test"]},
                timeout=30
            )
            
            # Log response details
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            try:
                logger.info(f"Response body: {response.text[:1000]}...")  # Only show first 1000 chars
            except Exception as e:
                logger.error(f"Error logging response body: {e}")
            
            # Check if successful
            if response.status_code in (200, 201):
                logger.info("✓ Memory creation API successful")
                
                try:
                    memory_data = response.json()
                    memory_id = memory_data.get("id")
                    logger.info(f"Created memory ID: {memory_id}")
                except Exception as e:
                    logger.error(f"Failed to parse response JSON: {e}")
            else:
                logger.error(f"✗ Memory creation API failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error during API request: {e}")
            logger.error(traceback.format_exc())
            return False
    
    except Exception as e:
        logger.error(f"✗ Failed to import requests module: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("A-MEM Memory Creation Debugger")
    logger.info("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("No valid OpenAI API key found in environment.")
        logger.warning("LLM-based memory operations may fail.")
    
    # Test options based on args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--direct":
            # Test just the direct memory creation
            direct_result = test_memory_creation_directly()
            if not direct_result:
                logger.error("Direct memory creation test failed.")
                return False
        elif sys.argv[1] == "--api":
            # Get port from args or default
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8903
            
            # Test just the API
            api_result = test_memory_creation_api(port)
            if not api_result:
                logger.error("API memory creation test failed.")
                return False
        else:
            logger.error(f"Unknown argument: {sys.argv[1]}")
            return False
    else:
        # Run both tests
        logger.info("Running full test suite...")
        
        # First test direct memory creation
        direct_result = test_memory_creation_directly()
        if not direct_result:
            logger.error("Direct memory creation test failed.")
            return False
        
        # Ask if server is running
        print("\nIs the server currently running? (y/n)")
        running = input().lower() == 'y'
        
        if running:
            # Get port
            print("Enter the server port (default: 8903):")
            try:
                port = int(input() or "8903")
            except ValueError:
                port = 8903
            
            # Test API
            api_result = test_memory_creation_api(port)
            if not api_result:
                logger.error("API memory creation test failed.")
                return False
        else:
            logger.info("Skipping API test as server is not running.")
    
    logger.info("\n✓ All executed tests passed successfully!")
    logger.info("Detailed logs have been saved to memory_creation_debug.log")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
