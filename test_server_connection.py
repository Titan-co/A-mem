#!/usr/bin/env python
"""
Test script to check if the server is running properly.
This runs before the integration test to ensure the server is accessible.
"""
import requests
import time
import sys
import os
import subprocess
import signal
import platform
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_server(port, max_retries=10, retry_interval=3):
    """Check if the server is running and responding on the given port"""
    print(f"Checking server on port {port}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}...")
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            
            if response.status_code == 200:
                print("\n✓ Server is running and responding correctly!")
                return True
                
            print(f"Server returned status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Connection error: {e}")
            
        if attempt < max_retries:
            print(f"Waiting {retry_interval} seconds before next attempt...")
            time.sleep(retry_interval)
    
    print("\n✗ Server is not responding after multiple attempts.")
    return False
    
def start_server(port):
    """Start the server in a subprocess"""
    print(f"Starting server on port {port}...")
    
    # Set environment variables
    env = os.environ.copy()
    env["DISABLE_CHROMADB"] = "true"
    
    # Construct command based on platform
    if platform.system() == "Windows":
        cmd = ["python", "-m", "uvicorn", "simple_server:app", "--host", "0.0.0.0", "--port", str(port)]
    else:
        cmd = ["python3", "-m", "uvicorn", "simple_server:app", "--host", "0.0.0.0", "--port", str(port)]
    
    # Start server process
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process
    
def main():
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8901"))
    
    # Start the server
    server_process = start_server(port)
    
    try:
        # Wait for server to start
        print(f"Waiting for server to start (max 30 seconds)...")
        time.sleep(5)  # Initial delay
        
        # Check if server is running
        if check_server(port, max_retries=5, retry_interval=5):
            print("Server check passed. Ready for integration test.")
            print("IMPORTANT: Leaving server running for integration test.")
            # Return success but DON'T terminate the server
            return 0
        else:
            print("Server failed to start properly.")
            # Only terminate if check failed
            if 'server_process' in locals() and server_process:
                print("Terminating server process...")
                if platform.system() == "Windows":
                    server_process.terminate()
                else:
                    server_process.send_signal(signal.SIGTERM)
                server_process.wait(timeout=5)
            return 1
    except Exception as e:
        print(f"Error during server check: {e}")
        # Terminate server on exception
        if 'server_process' in locals() and server_process:
            print("Terminating server process due to error...")
            if platform.system() == "Windows":
                server_process.terminate()
            else:
                server_process.send_signal(signal.SIGTERM)
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Server did not terminate gracefully, forcing...")
                server_process.kill()
        return 1
    
if __name__ == "__main__":
    sys.exit(main())
