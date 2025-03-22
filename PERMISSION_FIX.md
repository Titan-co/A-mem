# A-MEM Permission Issues Resolution

This document explains how to resolve permission issues when running the A-MEM MCP server.

## Problem

When running the A-MEM server, you may encounter permission errors like:

```
PermissionError: [Errno 13] Permission denied: 'C:\Users\username\.cache\chroma\onnx_models\...'
```

This happens because ChromaDB and SentenceTransformers try to download model files to your user cache directory, which may require elevated permissions.

## Solution

Several fixes have been implemented to resolve these issues:

1. **Local Cache Directories**: The system now uses project-local cache directories instead of user-wide ones.
2. **Cache Initialization Script**: Added `initialize_cache.py` to properly set up cache directories.
3. **Environment Variable Configuration**: Set environment variables to direct libraries to use our local cache.
4. **Fallback Mode**: Added a `DISABLE_CHROMADB` flag to run completely without ChromaDB.

## How to Use the Fixed Version

### Option 1: Run the new fixed script

```
run_fixed_server.bat
```

This script:
- Initializes cache directories
- Sets environment variables correctly
- Provides a safer "no ChromaDB" option

### Option 2: Use the original scripts 

The original scripts have been modified to initialize cache directories:
- `run_server_dynamic.bat`
- `run_claude_mcp_server.bat`
- `run_mcp_wrapper.bat`

### Option 3: Run with ChromaDB disabled

To completely bypass ChromaDB and use the fallback implementation:

```
set DISABLE_CHROMADB=true
python -m uvicorn simple_server:app --host 0.0.0.0 --port 8799
```

## Testing

The integration test has been enhanced to:
- Retry connections multiple times
- Provide better error messages
- Wait longer for server startup

## Cache Directory Structure

The new cache is stored in a `.cache` folder in the project directory:
- `.cache/chromadb_data` - ChromaDB persistence
- `.cache/sentence_transformers` - Sentence transformer models
- `.cache/transformers` - Hugging Face transformer models
- `.cache/onnx_models` - ONNX model files

## Troubleshooting

If you still encounter permission issues:
1. Try running the script with administrator privileges
2. Manually delete the `.cache` directory and let it recreate
3. Use the `DISABLE_CHROMADB=true` option to bypass ChromaDB completely
