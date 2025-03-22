# A-MEM MCP Server Debugging Guide

This document contains step-by-step instructions for debugging and running the A-MEM MCP Server.

## Common Issues and Solutions

### 1. File Encoding Issues

If you're seeing `UnicodeDecodeError`, it's likely due to file encoding issues, particularly on Windows systems using non-UTF-8 default encodings.

**Solution:**
- Ensure all Python files are saved with UTF-8 encoding
- When opening files in code, use explicit UTF-8 encoding:
  ```python
  with open(filepath, 'r', encoding='utf-8') as f:
      content = f.read()
  ```

### 2. Missing Dependencies

The server requires several dependencies to run properly.

**Solution:**
- Use a virtual environment to isolate dependencies
- Install all required packages:
  ```bash
  pip install -r requirements.txt
  pip install python-dotenv pydantic-settings fastapi uvicorn
  ```
- Make sure NLTK data is downloaded:
  ```python
  import nltk
  nltk.download('punkt')
  ```

### 3. Missing or Misconfigured .env File

The server needs a proper .env file to connect to OpenAI's API.

**Solution:**
- Create a .env file in the project root with:
  ```
  OPENAI_API_KEY=your_actual_api_key_here
  MODEL_NAME=all-MiniLM-L6-v2
  LLM_BACKEND=openai
  LLM_MODEL=gpt-4
  ```

### 4. Module Import Errors

If you're seeing import errors, it could be due to missing modules or Python path issues.

**Solution:**
- Check that all Python files are in the correct location
- Verify imports in each file match the actual module names
- Use absolute imports rather than relative imports

## Step-by-Step Debugging Process

1. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install python-dotenv pydantic-settings fastapi uvicorn
   ```

3. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

4. **Verify .env file**
   - Make sure it contains your real OpenAI API key
   - Check that other settings are properly configured

5. **Run the server with debug logging**
   ```bash
   python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug
   ```

6. **Common error messages and solutions:**

   - `ImportError: No module named 'module_name'`
     - Install the missing module: `pip install module_name`
   
   - `FileNotFoundError: [Errno 2] No such file or directory: '.env'`
     - Create the missing .env file in the project root
   
   - `ConnectionRefusedError: [WinError 10061]`
     - Port may be in use. Try a different port or stop the process using the current port

   - `UnicodeDecodeError`
     - Edit files to use UTF-8 encoding or specify encoding when opening files

## Checking Your Installation

Run the following script to check your installation:

```python
# save as check_installation.py
import importlib
import os

# Check key modules
modules = ["fastapi", "uvicorn", "pydantic", "python-dotenv", 
           "nltk", "openai", "sentence_transformers", 
           "chromadb", "rank_bm25"]
print("Checking modules:")
for module in modules:
    module_name = module.replace("-", "_")
    try:
        m = importlib.import_module(module_name)
        print(f"GOOD {module}")
    except ImportError as e:
        print(f"BAD {module}: {e}")

# Check files
files = ["server.py", "routes.py", "config.py", "models.py", 
         "memory_system.py", "llm_controller.py", "retrievers.py", ".env"]
print("\nChecking files:")
for file in files:
    if os.path.exists(file):
        print(f"GOOD {file} exists")
    else:
        print(f"BAD {file} missing")
```

## Testing the API

Once your server is running, test it with the following curl commands:

**Create a memory:**
```bash
curl -X POST "http://localhost:8000/api/v1/memories" -H "Content-Type: application/json" -d "{\"content\":\"Test memory content\",\"tags\":[\"test\"],\"category\":\"Testing\"}"
```

**Search memories:**
```bash
curl -X GET "http://localhost:8000/api/v1/search?query=test"
```

If these work, your server is functioning correctly!
