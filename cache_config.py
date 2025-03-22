"""
Global cache configuration for A-MEM
This needs to be imported before any other modules to set environment variables
"""
import os
import sys

# Get project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, ".cache")

# Create cache directories if they don't exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "chromadb_data"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "sentence_transformers"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "transformers"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "onnx_models"), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "tmp"), exist_ok=True)

# Set all cache-related environment variables
os.environ["CHROMADB_CACHE_DIR"] = CACHE_DIR
os.environ["CHROMADB_DIR"] = os.path.join(CACHE_DIR, "chromadb_data")
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(CACHE_DIR, "sentence_transformers")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(CACHE_DIR, "transformers")
os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "transformers")
os.environ["TMPDIR"] = os.path.join(CACHE_DIR, "tmp")
os.environ["XDG_CACHE_HOME"] = CACHE_DIR

# Patch ChromaDB's default path handling if possible
try:
    # Try to directly set the ChromaDB path before importing
    sys.path.insert(0, os.path.join(CACHE_DIR, "chromadb_path"))
except Exception as e:
    print(f"Warning: Could not patch ChromaDB paths: {e}")
