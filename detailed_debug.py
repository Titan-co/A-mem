#!/usr/bin/env python
"""
Detailed debugging script for A-MEM
This script will run comprehensive tests and generate detailed logs
to help diagnose server issues.
"""
import os
import sys
import json
import time
import traceback
import requests
from dotenv import load_dotenv
import importlib

# Configure detailed logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("detailed_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("detailed_debug")

def check_environment():
    """Check environment variables and settings"""
    logger.info("Checking environment variables...")
    
    # Load environment variables
    load_dotenv()
    
    # Check critical environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    api_url = os.getenv("OPENAI_API_URL")
    model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    llm_backend = os.getenv("LLM_BACKEND", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4")
    port = os.getenv("PORT", "8903")
    
    logger.info(f"OPENAI_API_KEY: {'[SET]' if api_key else '[NOT SET]'}")
    if api_key:
        # Mask key for security, just show first/last few chars
        masked_key = api_key[:4] + '...' + api_key[-4:] if len(api_key) > 8 else "[TOO SHORT]"
        logger.info(f"  API Key (masked): {masked_key}")
        if api_key == "your_openai_api_key_here":
            logger.error("  API Key is still set to the default value! This will cause LLM requests to fail.")
    else:
        logger.error("  No API key found. Set OPENAI_API_KEY in your .env file.")
    
    logger.info(f"OPENAI_API_URL: {'[SET to ' + api_url + ']' if api_url else '[NOT SET - using default OpenAI API]'}")
    logger.info(f"MODEL_NAME: {model_name}")
    logger.info(f"LLM_BACKEND: {llm_backend}")
    logger.info(f"LLM_MODEL: {llm_model}")
    logger.info(f"PORT: {port}")
    
    return {
        "api_key": api_key,
        "api_url": api_url,
        "model_name": model_name,
        "llm_backend": llm_backend,
        "llm_model": llm_model,
        "port": port
    }

def check_modules():
    """Check if all required modules are available"""
    logger.info("Checking required modules...")
    modules = [
        "fastapi", "uvicorn", "pydantic", "dotenv", "nltk", 
        "sentence_transformers", "chromadb", "openai", "numpy", "sklearn",
        "memory_system", "llm_controller", "retrievers"
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            logger.info(f"GOOD {module_name} imported successfully")
        except Exception as e:
            logger.error(f"BAD Error importing {module_name}: {e}")
            all_ok = False
    
    return all_ok

def check_cache_dirs():
    """Check if cache directories exist with proper permissions"""
    logger.info("Checking cache directories...")
    
    cache_dir = os.path.join(os.getcwd(), ".cache")
    if not os.path.exists(cache_dir):
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        try:
            os.makedirs(cache_dir, exist_ok=True)
            logger.info("Created cache directory")
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")
            return False
    
    # Check subdirectories
    subdirs = ["chromadb_data", "sentence_transformers", "transformers", "onnx_models"]
    for subdir in subdirs:
        subdir_path = os.path.join(cache_dir, subdir)
        if not os.path.exists(subdir_path):
            try:
                os.makedirs(subdir_path, exist_ok=True)
                logger.info(f"Created cache subdirectory: {subdir}")
            except Exception as e:
                logger.error(f"Failed to create {subdir} directory: {e}")
                return False
    
    # Check write permissions by creating a test file
    test_file_path = os.path.join(cache_dir, "test_write.txt")
    try:
        with open(test_file_path, 'w') as f:
            f.write("test")
        os.remove(test_file_path)
        logger.info("GOOD Cache directory is writable")
    except Exception as e:
        logger.error(f"BAD Cache directory is not writable: {e}")
        return False
    
    return True

def test_llm_connection(api_key, llm_model, api_url=None):
    """Test LLM connection by making a simple request"""
    logger.info("Testing LLM connection...")
    
    if not api_key or api_key == "your_openai_api_key_here":
        logger.error("Cannot test LLM connection: No valid API key found")
        return False
    
    try:
        from openai import OpenAI
        
        # Set up client kwargs
        client_kwargs = {"api_key": api_key}
        if api_url:
            client_kwargs["base_url"] = api_url
            logger.info(f"Using custom API URL: {api_url}")
        
        # Create client
        client = OpenAI(**client_kwargs)
        
        # Make a simple request
        logger.info(f"Testing with model: {llm_model}")
        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=10
        )
        
        # Check response
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            logger.info(f"GOOD LLM connection successful. Response: '{content}'")
            return True
        else:
            logger.error("BAD LLM response is empty or invalid")
            return False
            
    except Exception as e:
        logger.error(f"BAD LLM connection failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_memory_module():
    """Test memory system module initialization"""
    logger.info("Testing memory system module...")
    
    try:
        # Import memory system
        from memory_system import AgenticMemorySystem, strip_markdown_code_fences
        from config import settings
        
        # Try to initialize memory system (with error capture)
        try:
            logger.info("Initializing memory system...")
            logger.info(f"Settings: MODEL_NAME={settings.MODEL_NAME}, LLM_BACKEND={settings.LLM_BACKEND}, LLM_MODEL={settings.LLM_MODEL}")
            
            # Explicitly initialize with mock_evolution handler
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
            
            logger.info("GOOD Memory system initialized successfully")
            
            # Test analyze_content method
            logger.info("Testing content analysis...")
            try:
                test_content = "This is a test content for analysis"
                
                logger.info("Triggering content analysis")
                analysis_result = memory_system.analyze_content(test_content)
                
                logger.info(f"GOOD Content analysis successful: {json.dumps(analysis_result)}")
                
                # Now test memory creation
                logger.info("Testing memory creation...")
                memory_id = memory_system.create(
                    content=test_content,
                    tags=["test", "debug"],
                    category="Testing"
                )
                
                logger.info(f"GOOD Memory created with ID: {memory_id}")
                
                # Read the memory
                memory = memory_system.read(memory_id)
                logger.info(f"GOOD Memory read successful: {memory.id}")
                logger.info(f"  Content: {memory.content}")
                logger.info(f"  Tags: {memory.tags}")
                logger.info(f"  Context: {memory.context}")
                
                return True
                
            except Exception as e:
                logger.error(f"BAD Content analysis failed: {e}")
                logger.error(traceback.format_exc())
                return False
                
        except Exception as e:
            logger.error(f"BAD Memory system initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"BAD Memory system module import failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_server_api(port):
    """Test server API endpoints"""
    logger.info("Testing server API...")
    
    base_url = f"http://localhost:{port}"
    logger.info(f"Server URL: {base_url}")
    
    # Test health endpoint
    try:
        logger.info("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code != 200:
            logger.error("BAD Health check failed")
            return False
        else:
            logger.info("GOOD Health check passed")
    except Exception as e:
        logger.error(f"BAD Health check error: {e}")
        return False
    
    # Test memory creation with very detailed error capturing
    try:
        logger.info("Testing memory creation endpoint...")
        test_content = f"Test memory created during debug at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Prepare request and set timeout to 30 seconds
        response = requests.post(
            f"{base_url}/api/v1/memories",
            json={"content": test_content, "tags": ["debug", "test"]},
            timeout=30
        )
        
        # Log complete response details
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Headers: {response.headers}")
        
        # Log response content safely
        try:
            if response.text:
                logger.info(f"Response text: {response.text[:1000]}...")  # Limit to first 1000 chars
                
                # Try to parse as JSON
                if 'application/json' in response.headers.get('Content-Type', ''):
                    try:
                        json_response = response.json()
                        logger.info(f"Parsed JSON: {json.dumps(json_response)[:1000]}...")
                    except Exception as e:
                        logger.error(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"Error logging response: {e}")
        
        # Check response
        if response.status_code not in (200, 201):
            logger.error(f"BAD Memory creation failed with status {response.status_code}")
            return False
        else:
            logger.info("GOOD Memory creation successful")
            
            # Extract memory ID
            try:
                memory_data = response.json()
                memory_id = memory_data.get("id")
                logger.info(f"Memory ID: {memory_id}")
                
                # Test search endpoint
                logger.info("Testing search endpoint...")
                search_response = requests.get(
                    f"{base_url}/api/v1/search",
                    params={"query": "debug test", "k": 5},
                    timeout=30
                )
                
                logger.info(f"Search status code: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    results = search_data.get("results", [])
                    logger.info(f"Found {len(results)} results")
                    logger.info("GOOD Search successful")
                else:
                    logger.error("BAD Search failed")
            except Exception as e:
                logger.error(f"Error processing memory ID or searching: {e}")
                logger.error(traceback.format_exc())
                return False
            
            return True
    except requests.exceptions.Timeout:
        logger.error("BAD Memory creation timed out after 30 seconds")
        return False
    except Exception as e:
        logger.error(f"BAD Memory creation error: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run all diagnostics"""
    logger.info("=" * 60)
    logger.info("A-MEM Detailed Diagnostic Tool")
    logger.info("=" * 60)
    
    # Check environment
    env_data = check_environment()
    
    # Check modules
    modules_ok = check_modules()
    
    # Check cache directories
    cache_ok = check_cache_dirs()
    
    # Test LLM connection if we have an API key
    if env_data["api_key"] and env_data["api_key"] != "your_openai_api_key_here":
        llm_ok = test_llm_connection(
            env_data["api_key"], 
            env_data["llm_model"],
            env_data["api_url"]
        )
    else:
        logger.warning("Skipping LLM connection test due to missing API key")
        llm_ok = False
    
    # Test memory module
    memory_ok = test_memory_module()
    
    # Test the server API if specified
    server_running = False
    if len(sys.argv) > 1 and sys.argv[1] == "--test-server":
        logger.info("Testing server API as requested...")
        server_ok = test_server_api(env_data["port"])
    else:
        logger.info("Skipping server API test (use --test-server to include)")
        server_ok = None
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Diagnostic Summary")
    logger.info("=" * 60)
    logger.info(f"Environment: {'GOOD' if env_data['api_key'] else 'BAD'}")
    logger.info(f"Modules: {'GOOD' if modules_ok else 'BAD'}")
    logger.info(f"Cache Directories: {'GOOD' if cache_ok else 'BAD'}")
    logger.info(f"LLM Connection: {'GOOD' if llm_ok else 'BAD'}")
    logger.info(f"Memory Module: {'GOOD' if memory_ok else 'BAD'}")
    if server_ok is not None:
        logger.info(f"Server API: {'GOOD' if server_ok else 'BAD'}")
    
    logger.info("\nDetailed logs have been saved to detailed_debug.log")
    
    # Return success status
    return modules_ok and cache_ok and memory_ok and (server_ok if server_ok is not None else True)

if __name__ == "__main__":
    success = main()
    if not success:
        logger.warning("Some diagnostics failed. Review the logs for details.")
        sys.exit(1)
    else:
        logger.info("All diagnostics passed successfully!")
        sys.exit(0)
