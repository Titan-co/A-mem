import sys
import traceback
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("debug")

def main():
    logger.info("Starting debug process for A-MEM server")
    
    # Check environment
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check .env file
    if os.path.exists(".env"):
        logger.info(".env file exists")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info(".env file loaded successfully")
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    else:
        logger.error(".env file does not exist")
    
    # Try importing key modules
    modules_to_check = [
        "fastapi", "uvicorn", "pydantic", "dotenv", 
        "nltk", "openai", "sentence_transformers", 
        "chromadb", "sklearn"
    ]
    
    for module in modules_to_check:
        try:
            __import__(module)
            logger.info(f"Successfully imported {module}")
        except ImportError as e:
            logger.error(f"Error importing {module}: {e}")
    
    # Try importing application modules
    app_modules = [
        "memory_system", "llm_controller", "retrievers",
        "models", "routes", "config", "utils"
    ]
    
    for module in app_modules:
        try:
            __import__(module)
            logger.info(f"Successfully imported {module}")
        except ImportError as e:
            logger.error(f"Error importing {module}: {e}")
        except Exception as e:
            logger.error(f"Error in {module}: {e}")
            logger.error(traceback.format_exc())
    
    # Try to import and run the server module
    try:
        logger.info("Attempting to import server module")
        import server
        logger.info("Server module imported successfully")
        
        # Check if app exists in server module
        if hasattr(server, 'app'):
            logger.info("FastAPI app found in server module")
        else:
            logger.error("No FastAPI app found in server module")
        
        logger.info("The server seems to be properly set up")
        logger.info("Now attempting to run the server...")
        
        try:
            import uvicorn
            logger.info("Starting server with uvicorn")
            # Run for a very short time to check for immediate errors
            uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="debug")
        except Exception as e:
            logger.error(f"Error running server: {e}")
            logger.error(traceback.format_exc())
            
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error in server module: {e}")
        logger.error(traceback.format_exc())
    
    logger.info("Debug process completed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(traceback.format_exc())
        
    print("\nDebug process completed. Check server_debug.log for details.")
