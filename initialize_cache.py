#!/usr/bin/env python
"""
Initialize cache directories for A-MEM
This script creates the necessary cache directories with appropriate permissions
"""
import os
import sys
import shutil

def initialize_cache():
    """Create cache directories with proper permissions"""
    print("Initializing A-MEM cache directories...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(project_dir, ".cache")
    
    # Create subdirectories
    subdirs = [
        "chromadb_data",
        "sentence_transformers",
        "transformers",
        "onnx_models"
    ]
    
    # Remove old cache if it exists
    if os.path.exists(cache_dir):
        try:
            print(f"Removing old cache directory: {cache_dir}")
            shutil.rmtree(cache_dir)
            print("Old cache removed successfully")
        except Exception as e:
            print(f"Error removing old cache: {e}")
            print("Continuing anyway...")
    
    # Create main cache directory
    try:
        os.makedirs(cache_dir, exist_ok=True)
        print(f"Created main cache directory: {cache_dir}")
    except Exception as e:
        print(f"Error creating cache directory: {e}")
        return False
    
    # Create subdirectories
    for subdir in subdirs:
        try:
            subdir_path = os.path.join(cache_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            print(f"Created cache subdirectory: {subdir_path}")
        except Exception as e:
            print(f"Error creating {subdir} directory: {e}")
    
    print("Cache initialization complete!")
    return True

if __name__ == "__main__":
    result = initialize_cache()
    sys.exit(0 if result else 1)
