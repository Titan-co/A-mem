"""Test if all required modules can be imported correctly"""
import sys
import traceback

def test_import(module_name):
    try:
        module = __import__(module_name)
        return f"✓ {module_name} imported successfully"
    except Exception as e:
        return f"✗ {module_name}: {str(e)}\n{traceback.format_exc()}"

# List of modules to test
modules = [
    # System modules
    "fastapi",
    "uvicorn",
    "pydantic",
    "dotenv",
    "nltk",
    "openai",
    "sentence_transformers",
    "chromadb",
    "sklearn",
    
    # Application modules
    "memory_system",
    "llm_controller",
    "retrievers",
    "models",
    "routes",
    "config",
    "utils",
    "server"
]

print("Testing module imports...")
for module_name in modules:
    result = test_import(module_name)
    print(result)
    print("-" * 50)

print("\nTest complete!")
