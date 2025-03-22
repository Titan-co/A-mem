#!/usr/bin/env python
"""
Diagnostic tool for A-MEM server
This script checks all dependencies and environment variables
"""
import sys
import os
import platform
import importlib.util
import socket
import subprocess
import traceback
from importlib.metadata import version

def check_port(port):
    """Check if the port is available or already in use"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        return True  # Port is available
    except socket.error:
        return False  # Port is in use
    finally:
        s.close()

def check_module_version(module_name):
    """Check if a module is installed and get its version"""
    try:
        return version(module_name)
    except Exception:
        try:
            # Try importing it directly
            module = importlib.import_module(module_name)
            return getattr(module, "__version__", "unknown")
        except ImportError:
            return None

def main():
    print("=" * 60)
    print("A-MEM Server Diagnostics")
    print("=" * 60)
    
    # System information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check .env file
    print("\nChecking .env file:")
    if os.path.exists(".env"):
        print("✓ .env file exists")
        try:
            with open(".env", "r") as f:
                env_content = f.read()
                port_line = next((line for line in env_content.splitlines() if line.startswith("PORT=")), None)
                if port_line:
                    port = port_line.split("=")[1].strip()
                    print(f"✓ Port specified in .env: {port}")
                    
                    # Check if port is available
                    if check_port(int(port)):
                        print(f"✓ Port {port} is available")
                    else:
                        print(f"✗ Port {port} is already in use")
                        # List processes using this port
                        if platform.system() == "Windows":
                            try:
                                result = subprocess.run(["netstat", "-ano", "|", "findstr", f":{port}"], 
                                                       capture_output=True, text=True, shell=True)
                                if result.stdout:
                                    print(f"Processes using port {port}:")
                                    print(result.stdout)
                            except Exception as e:
                                print(f"Error checking processes: {e}")
                else:
                    print("✗ No PORT defined in .env file")
        except Exception as e:
            print(f"✗ Error reading .env file: {e}")
    else:
        print("✗ .env file not found")
    
    # Check dependencies
    print("\nChecking dependencies:")
    dependencies = [
        "fastapi", "uvicorn", "pydantic", "dotenv", "nltk", 
        "sentence_transformers", "chromadb", "openai"
    ]
    
    for dep in dependencies:
        version = check_module_version(dep)
        if version:
            print(f"✓ {dep} (version: {version})")
        else:
            print(f"✗ {dep} not found")
    
    # Check cache directory
    print("\nChecking cache directory:")
    cache_dir = os.path.join(os.getcwd(), ".cache")
    if os.path.exists(cache_dir):
        print(f"✓ Cache directory exists: {cache_dir}")
        # Check subdirectories
        subdirs = ["chromadb_data", "sentence_transformers", "transformers", "onnx_models"]
        for subdir in subdirs:
            subdir_path = os.path.join(cache_dir, subdir)
            if os.path.exists(subdir_path):
                print(f"✓ Subdirectory exists: {subdir}")
            else:
                print(f"✗ Subdirectory missing: {subdir}")
    else:
        print(f"✗ Cache directory not found: {cache_dir}")
    
    # Check for server process
    print("\nChecking for running server:")
    # Get port from .env or use default
    port = "8901"  # Default
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
            port_line = next((line for line in env_content.splitlines() if line.startswith("PORT=")), None)
            if port_line:
                port = port_line.split("=")[1].strip()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', int(port)))
        if result == 0:
            print(f"✓ Server is running on port {port}")
            # Try to get health check
            try:
                import requests
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✓ Server health check passed")
                else:
                    print(f"✗ Server health check failed: Status {response.status_code}")
            except Exception as e:
                print(f"✗ Health check error: {e}")
        else:
            print(f"✗ No server running on port {port}")
    except Exception as e:
        print(f"✗ Error checking server: {e}")
    finally:
        sock.close()
    
    print("\nDiagnostics complete!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running diagnostics: {e}")
        traceback.print_exc()
