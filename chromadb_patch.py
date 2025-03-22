"""
Monkey patching for ChromaDB's internal path handling
This file needs to be imported before chromadb to patch its path functions
"""
import os
import sys
import logging
import importlib
import importlib.util

# Configure logging
logger = logging.getLogger("chromadb_patch")

# Get project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, ".cache")

# Create cache directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "chromadb_data"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "onnx_models"), exist_ok=True)

# Find the chromadb package path if it's installed
chromadb_path = None
try:
    chromadb_spec = importlib.util.find_spec("chromadb")
    if chromadb_spec and chromadb_spec.origin:
        chromadb_path = os.path.dirname(chromadb_spec.origin)
        logger.info(f"Found chromadb at: {chromadb_path}")
except Exception as e:
    logger.error(f"Could not find chromadb package: {e}")

# Function to patch chromadb paths
def patch_chromadb():
    """Patches ChromaDB's path handling to use our local cache"""
    global chromadb_path
    
    # Set environment variables
    os.environ["CHROMADB_CACHE_DIR"] = CACHE_DIR
    os.environ["CHROMADB_DIR"] = os.path.join(CACHE_DIR, "chromadb_data")
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(CACHE_DIR, "sentence_transformers")
    os.environ["TRANSFORMERS_CACHE"] = os.path.join(CACHE_DIR, "transformers")
    os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "transformers")
    os.environ["TMPDIR"] = os.path.join(CACHE_DIR, "tmp")
    os.environ["XDG_CACHE_HOME"] = CACHE_DIR
    
    # Direct imports for patching
    try:
        if chromadb_path:
            # Find embedding functions module
            embedding_module_path = os.path.join(chromadb_path, "utils", "embedding_functions.py")
            if os.path.exists(embedding_module_path):
                logger.info(f"Found embedding_functions.py at: {embedding_module_path}")
                
                # Read the file and look for path definitions
                with open(embedding_module_path, 'r') as f:
                    content = f.read()
                    
                if "default_path = Path.home()" in content:
                    logger.info("Found default_path definition in embedding_functions.py")
                    
                    # Could modify the file directly here, but that might be risky
                    # Instead, we'll use importlib hooks in the future
                
            else:
                logger.warning(f"Could not find embedding_functions.py in {chromadb_path}")
                
            # Also look for direct references to .cache directory
            import glob
            python_files = glob.glob(os.path.join(chromadb_path, "**", "*.py"), recursive=True)
            for file in python_files:
                with open(file, 'r', errors='ignore') as f:
                    try:
                        content = f.read()
                        if ".cache/chroma" in content:
                            logger.info(f"Found .cache/chroma reference in: {file}")
                    except Exception as e:
                        logger.error(f"Error reading {file}: {e}")
    except Exception as e:
        logger.error(f"Error during chromadb path analysis: {e}")
    
    # Method 2: Import and patch at runtime
    try:
        # Import actual module to patch
        import chromadb.utils.embedding_functions as embed_funcs
        
        # Create a backup of the original
        original_DefaultEmbeddingFunction = embed_funcs.DefaultEmbeddingFunction
        
        # Define a patched version
        class PatchedDefaultEmbeddingFunction(original_DefaultEmbeddingFunction):
            def __init__(self, *args, **kwargs):
                # Override the default cache path
                self.cache_dir = os.path.join(CACHE_DIR, "onnx_models")
                super().__init__(*args, **kwargs)
                
            def _download_model_if_not_exists(self):
                """Override the default download path"""
                # Redirect downloads to our cache
                self.DOWNLOAD_PATH = self.cache_dir
                
                # Call the original method
                try:
                    super()._download_model_if_not_exists()
                except Exception as e:
                    logger.error(f"Error in patched _download_model_if_not_exists: {e}")
                    
        # Replace the original with our patched version
        embed_funcs.DefaultEmbeddingFunction = PatchedDefaultEmbeddingFunction
        logger.info("Successfully patched DefaultEmbeddingFunction")
        
    except Exception as e:
        logger.error(f"Error patching DefaultEmbeddingFunction: {e}")

# Run patching when imported
patch_chromadb()
