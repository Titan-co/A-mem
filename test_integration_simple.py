#!/usr/bin/env python
"""
Simplified integration test for A-MEM MCP Server
This test assumes the server is already running and verified
"""
import json
import sys
import time
import requests
import traceback
import os
import subprocess
import platform
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_server(port):
    """Cleanup server processes using the specified port"""
    print(f"\nCleaning up server on port {port}...")
    
    try:
        if platform.system() == "Windows":
            # Windows cleanup approach
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", f":{port}"], 
                capture_output=True, text=True, shell=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f":{port}" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            print(f"Found process using port {port}: PID {pid}")
                            try:
                                subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
                                print(f"Successfully terminated process with PID {pid}")
                            except subprocess.CalledProcessError as e:
                                print(f"Failed to terminate process: {e}")
            else:
                print(f"No processes found using port {port}")
        else:
            # Unix-like systems
            try:
                result = subprocess.run(
                    ["lsof", "-i", f":{port}"], 
                    capture_output=True, text=True, check=True
                )
                
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # First line is header
                    for line in lines[1:]:  # Skip header
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            print(f"Found process using port {port}: PID {pid}")
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"Successfully terminated process with PID {pid}")
                            except OSError as e:
                                print(f"Failed to terminate process: {e}")
            except subprocess.CalledProcessError:
                print(f"No processes found using port {port}")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        traceback.print_exc()

def test_server():
    """Run a series of API tests against the running server"""
    # Get port from environment or use default
    port = os.getenv("PORT", "8901")
    base_url = f"http://localhost:{port}"
    api_url = f"{base_url}/api/v1"
    
    print("=" * 60)
    print("A-MEM Server Integration Test")
    print("=" * 60)
    print(f"Testing server at {base_url}")
    
    try:
        # Test 1: Health check
        try:
            print("\nTest 1: Health check")
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✓ Health check passed")
            else:
                print(f"✗ Health check failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check error: {e}")
            return False
        
        # Test 2: Create memory
        try:
            print("\nTest 2: Create memory")
            test_content = f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            response = requests.post(
                f"{api_url}/memories",
                json={
                    "content": test_content,
                    "tags": ["test", "integration"],
                    "category": "Testing"
                },
                timeout=30  # Longer timeout for memory creation
            )
            
            if response.status_code not in (200, 201):
                print(f"✗ Create memory failed: Status {response.status_code}")
                print(response.text)
                return False
                
            memory_data = response.json()
            memory_id = memory_data.get("id")
            
            if not memory_id:
                print("✗ Create memory failed: No memory ID returned")
                return False
                
            print(f"✓ Created memory with ID: {memory_id}")
            print(f"  Content: {memory_data.get('content', 'N/A')}")
        except Exception as e:
            print(f"✗ Create memory error: {e}")
            traceback.print_exc()
            return False
        
        # Test 3: Search memories
        try:
            print("\nTest 3: Search memories")
            response = requests.get(
                f"{api_url}/search",
                params={"query": "test", "k": 5},
                timeout=30  # Longer timeout for search
            )
            
            if response.status_code != 200:
                print(f"✗ Search memories failed: Status {response.status_code}")
                print(response.text)
                return False
                
            search_results = response.json().get("results", [])
            print(f"✓ Found {len(search_results)} results")
            
            if len(search_results) > 0:
                result = search_results[0]
                print(f"  Top result: {result.get('content', 'N/A')[:50]}...")
        except Exception as e:
            print(f"✗ Search memories error: {e}")
            traceback.print_exc()
            return False
        
        print("\n✓ All tests passed successfully!")
        return True
    
    finally:
        # Clean up server process
        cleanup_server(port)

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
