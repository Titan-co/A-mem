import sys
import os
import importlib
import importlib.util

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Check key modules
modules = ["fastapi", "uvicorn", "pydantic", "dotenv", 
           "nltk", "openai", "sentence_transformers", 
           "chromadb", "rank_bm25"]
print("\nChecking modules:")
for module in modules:
    try:
        m = importlib.import_module(module)
        version = getattr(m, "__version__", "unknown")
        print(f"✓ {module} (version: {version})")
    except ImportError as e:
        print(f"✗ {module}: {e}")

# Check files
files = ["server.py", "routes.py", "config.py", "models.py", 
         "memory_system.py", "llm_controller.py", "retrievers.py"]
print("\nChecking files:")
for file in files:
    if os.path.exists(file):
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} missing")

# Check NLTK data
try:
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
        print("\n✓ NLTK punkt tokenizer found")
    except LookupError:
        print("\n✗ NLTK punkt tokenizer not found")
except ImportError:
    pass  # Already reported above

# Check .env file
if os.path.exists(".env"):
    print("\n✓ .env file exists")
    # Check if API key is set
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            if "OPENAI_API_KEY=" in content and "OPENAI_API_KEY=your" not in content:
                print("  ✓ API key appears to be set")
            else:
                print("  ✗ API key may not be properly set")
    except Exception as e:
        print(f"  ✗ Error reading .env file: {e}")
else:
    print("\n✗ .env file missing")

# Try to import the server module
try:
    print("\nTrying to import server module:")
    spec = importlib.util.find_spec("server")
    if spec is not None:
        print("✓ Server module found at", spec.origin)
    else:
        print("✗ Server module not found in Python path")
except ImportError as e:
    print(f"✗ Error importing server module: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
