"""Inspect the server.py file to see if it has the expected structure"""
import os
import sys
import importlib.util
import inspect
import traceback

def inspect_file(filename):
    """Inspect a Python file and report its structure"""
    if not os.path.exists(filename):
        return f"File {filename} does not exist"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
            print(f"File size: {len(source)} bytes")
            lines = source.split('\n')
            print(f"Line count: {len(lines)}")
            
            # Look for key patterns
            patterns = {
                "FastAPI import": "from fastapi import FastAPI",
                "app definition": "app = FastAPI",
                "CORS middleware": "CORSMiddleware",
                "router include": "app.include_router",
                "uvicorn import": "import uvicorn",
                "uvicorn.run": "uvicorn.run",
            }
            
            for name, pattern in patterns.items():
                found = any(pattern in line for line in lines)
                print(f"{name}: {'Found' if found else 'Not found'}")
            
            # Print the first few non-empty lines
            print("\nFirst 10 non-empty lines:")
            count = 0
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    print(f"  {line.strip()}")
                    count += 1
                    if count >= 10:
                        break
            
            return "File inspection complete"
    except Exception as e:
        return f"Error inspecting file: {e}\n{traceback.format_exc()}"

def import_module(module_name, filename):
    """Try to import a module and inspect its contents"""
    try:
        # Try to import as a module
        spec = importlib.util.spec_from_file_location(module_name, filename)
        if spec is None:
            return f"Could not create module spec for {filename}"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for FastAPI app
        app = None
        for name, obj in inspect.getmembers(module):
            if name == 'app':
                app = obj
                break
        
        if app is None:
            return f"No 'app' variable found in {module_name}"
        
        # Check app type
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print(f"Found FastAPI app: {app.title or 'Untitled'} v{app.version or 'unknown'}")
            print(f"Routes: {len(app.routes)}")
            print("\nEndpoints:")
            for route in app.routes:
                print(f"  {route.path}: {route.methods}")
            
            return "Module inspection complete"
        else:
            return f"'app' variable is not a FastAPI instance: {type(app)}"
    except Exception as e:
        return f"Error importing module: {e}\n{traceback.format_exc()}"

def main():
    filename = 'server.py'
    print(f"Inspecting {filename}...")
    print("-" * 50)
    
    # Inspect file content
    result = inspect_file(filename)
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    # Try to import and inspect module
    print(f"Trying to import {filename} as a module...")
    module_result = import_module('server', filename)
    print("-" * 50)
    print(module_result)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
    
    print("\nInspection complete.")
