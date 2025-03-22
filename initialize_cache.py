#!/usr/bin/env python
"""Initialize cache directories for A-MEM
This script creates the necessary cache directories with appropriate permissions

It handles the ChromaDB cache directory structure and ensures all the right paths
are created for embedding functions to work properly.
"""
import os
import sys
import shutil
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cache_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cache_setup")

def check_directory_writable(directory):
    """Check if a directory is writable by creating a test file"""
    if not os.path.exists(directory):
        return False
        
    try:
        test_file = os.path.join(directory, ".write_test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception as e:
        logger.warning(f"Directory {directory} is not writable: {e}")
        return False

def initialize_cache(force_recreate=False):
    """Create cache directories with proper permissions
    
    Args:
        force_recreate: If True, remove existing cache directories first
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    logger.info("Initializing A-MEM cache directories...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(project_dir, ".cache")
    
    # Create detailed subdirectory structure
    subdirs = [
        # ChromaDB data
        "chromadb_data",
        "chromadb_data/index",
        "chromadb_data/embeddings",
        
        # Model caches
        "sentence_transformers",
        "transformers",
        "onnx_models",
        "onnx_models/all-MiniLM-L6-v2",
        "onnx_models/all-MiniLM-L6-v2/onnx",
        
        # Additional dirs that might be needed
        "tmp"
    ]
    
    # Remove old cache if requested
    if force_recreate and os.path.exists(cache_dir):
        try:
            logger.info(f"Removing old cache directory: {cache_dir}")
            shutil.rmtree(cache_dir)
            logger.info("Old cache removed successfully")
        except Exception as e:
            logger.error(f"Error removing old cache: {e}")
            logger.info("Will attempt to continue anyway...")
    
    # Create main cache directory
    try:
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Created main cache directory: {cache_dir}")
    except Exception as e:
        logger.error(f"Error creating cache directory: {e}")
        return False
    
    # Create subdirectories
    success = True
    for subdir in subdirs:
        try:
            subdir_path = os.path.join(cache_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            logger.info(f"Created cache subdirectory: {subdir_path}")
            
            # Verify we can write to the directory
            if not check_directory_writable(subdir_path):
                logger.error(f"Directory {subdir_path} exists but is not writable!")
                success = False
        except Exception as e:
            logger.error(f"Error creating {subdir} directory: {e}")
            success = False
    
    # Create .env files to help other tools find these paths
    try:
        env_file = os.path.join(cache_dir, ".env")
        with open(env_file, 'w') as f:
            f.write(f"CHROMADB_CACHE_DIR={cache_dir}\n")
            f.write(f"SENTENCE_TRANSFORMERS_HOME={os.path.join(cache_dir, 'sentence_transformers')}\n")
            f.write(f"TRANSFORMERS_CACHE={os.path.join(cache_dir, 'transformers')}\n")
            f.write(f"TMPDIR={os.path.join(cache_dir, 'tmp')}\n")
        logger.info(f"Created environment file at {env_file}")
    except Exception as e:
        logger.error(f"Error creating environment file: {e}")
        success = False
    
    # Set environment variables for this process
    os.environ["CHROMADB_CACHE_DIR"] = cache_dir
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(cache_dir, "sentence_transformers")
    os.environ["TRANSFORMERS_CACHE"] = os.path.join(cache_dir, "transformers")
    os.environ["TMPDIR"] = os.path.join(cache_dir, "tmp")
    
    if success:
        logger.info("Cache initialization complete!")
    else:
        logger.warning("Cache initialization completed with some errors.")
    
    return success

def test_cache_access():
    """Test if we can properly access the cache directories"""
    logger.info("Testing cache directory access...")
    
    # Get cache directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(project_dir, ".cache")
    
    # Check key directories
    key_dirs = [
        cache_dir,
        os.path.join(cache_dir, "chromadb_data"),
        os.path.join(cache_dir, "onnx_models")
    ]
    
    all_ok = True
    for directory in key_dirs:
        if os.path.exists(directory):
            if check_directory_writable(directory):
                logger.info(f"[OK] {directory} exists and is writable")
            else:
                logger.error(f"[ERROR] {directory} exists but is not writable")
                all_ok = False
        else:
            logger.error(f"[ERROR] {directory} does not exist")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    # Check for command line arguments
    force_recreate = "--force" in sys.argv
    test_only = "--test" in sys.argv
    
    if test_only:
        # Just test access
        result = test_cache_access()
    else:
        # Initialize cache
        result = initialize_cache(force_recreate)
        # Then test access
        access_ok = test_cache_access()
        result = result and access_ok
    
    # Show directory contents for debugging
    if "--verbose" in sys.argv:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(project_dir, ".cache")
        logger.info(f"Cache directory contents:")
        for root, dirs, files in os.walk(cache_dir):
            level = root.replace(cache_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                logger.info(f"{sub_indent}{f}")
    
    # Exit with appropriate status code
    logger.info(f"Cache setup {'succeeded' if result else 'failed'}")
    sys.exit(0 if result else 1)
