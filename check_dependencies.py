import sys
import os
import importlib
import pkg_resources

def check_module(module_name, min_version=None):
    """Check if a module is installed and meets the minimum version requirement."""
    try:
        # Try to import the module
        module = importlib.import_module(module_name.replace("-", "_"))
        
        # Get the version
        if hasattr(module, "__version__"):
            version = module.__version__
        elif hasattr(module, "VERSION"):
            version = module.VERSION
        elif hasattr(module, "version"):
            version = module.version
        else:
            # Try to get version from pkg_resources
            try:
                version = pkg_resources.get_distribution(module_name).version
            except:
                version = "unknown"
        
        # Check if version meets minimum requirement
        if min_version and version != "unknown":
            from packaging import version as pkg_version
            if pkg_version.parse(version) < pkg_version.parse(min_version):
                return f"✗ {module_name} (installed: {version}, required: {min_version})"
        
        return f"✓ {module_name} (version: {version})"
    except ImportError as e:
        return f"✗ {module_name}: {e}"
    except Exception as e:
        return f"? {module_name}: {e}"

def main():
    print(f"Python version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Required modules with minimum versions
    modules = [
        ("fastapi", "0.95.0"),
        ("uvicorn", "0.20.0"),
        ("pydantic", "2.0.0"),
        ("python-dotenv", "1.0.0"),
        ("nltk", "3.8.0"),
        ("openai", "1.0.0"),
        ("sentence-transformers", "2.2.2"),
        ("chromadb", "0.4.0"),
        ("rank-bm25", "0.2.0"),
        ("transformers", "4.30.0"),
        ("litellm", "1.5.0"),
        ("numpy", "1.20.0"),
        ("scikit-learn", "1.0.0")
    ]
    
    # Module import names can differ from package names
    module_name_mapping = {
        "python-dotenv": "dotenv",
        "sentence-transformers": "sentence_transformers",
        "rank-bm25": "rank_bm25",
        "scikit-learn": "sklearn"
    }
    
    print("\nChecking dependencies:")
    for module, min_version in modules:
        actual_module = module_name_mapping.get(module, module)
        result = check_module(actual_module, min_version)
        print(f"{result} (package: {module})")
    
    # Check if key files exist
    key_files = [
        "server.py",
        "routes.py",
        "config.py",
        "models.py",
        "memory_system.py",
        "llm_controller.py",
        "retrievers.py",
        "requirements.txt",
        ".env"
    ]
    
    print("\nChecking key files:")
    for file in key_files:
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
            print("\n✗ NLTK punkt tokenizer not found. Run 'nltk.download(\"punkt\")'")
    except ImportError:
        # Already reported above
        pass
    
    # Check OpenAI API key
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and not api_key.startswith(("sk-test", "your", "sk_test")):
                print("\n✓ OpenAI API key appears to be properly set")
            else:
                print("\n✗ OpenAI API key is missing or invalid")
        except Exception as e:
            print(f"\n✗ Error checking OpenAI API key: {e}")
    else:
        print("\n✗ .env file missing")

if __name__ == "__main__":
    main()
