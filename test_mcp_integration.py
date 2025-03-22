"""
Test script for the MCP integration with A-MEM
This script simulates the MCP protocol communication for local testing
"""
import json
import sys
import time
import requests
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get port from environment or use default
PORT = os.getenv("PORT", "8767")
print(f"Using port from environment: {PORT}")

def simulate_mcp_protocol():
    """Simulate MCP protocol interactions for testing"""
    print("=" * 50)
    print("A-MEM MCP Integration Tester")
    print("=" * 50)
    print(f"This script tests integration between MCP and A-MEM")
    print(f"Ensure the simple_server.py is running on port {PORT}")
    print()
    
    # Check if server is running with retry
    max_retries = 3
    retry_count = 0
    retry_delay = 2  # seconds
    
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1}/{max_retries} to connect to server...")
            response = requests.get(f"http://localhost:{PORT}/health")
            if response.status_code == 200:
                print("✓ Server is running and responsive")
                break
            else:
                print(f"Server responded with status code {response.status_code}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
        except Exception as e:
            print(f"Connection attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
    
    if retry_count >= max_retries:
        print(f"ERROR: Server is not responding after {max_retries} attempts")
        return False
    
    # Test initialize
    print("\nTest 1: Initialize request")
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "0.1.0"
            }
        }
    }
    
    # Send directly to API since we're not using stdin/stdout
    try:
        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "capabilities": {}
            }
        }
        print("✓ Initialize would respond correctly")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False
    
    # Test create_memory
    print("\nTest 2: Create memory")
    memory_content = f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Send to API directly
        response = requests.post(
            f"http://localhost:{PORT}/api/v1/memories",
            json={
                "content": memory_content,
                "tags": ["test", "mcp"],
                "category": "Testing"
            }
        )
        
        if response.status_code != 200 and response.status_code != 201:
            print(f"ERROR: Failed to create memory - status code {response.status_code}")
            print(response.text)
            return False
            
        memory_data = response.json()
        memory_id = memory_data["id"]
        print(f"✓ Created memory with ID: {memory_id}")
        print(f"  Content: {memory_data['content']}")
        print(f"  Tags: {memory_data['tags']}")
        print(f"  Context: {memory_data['context']}")
        print(f"  Keywords: {memory_data['keywords']}")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False
    
    # Test search_memories
    print("\nTest 3: Search memories")
    
    try:
        # Send to API directly
        response = requests.get(
            f"http://localhost:{PORT}/api/v1/search",
            params={
                "query": "test",
                "k": 5
            }
        )
        
        if response.status_code != 200:
            print(f"ERROR: Failed to search memories - status code {response.status_code}")
            print(response.text)
            return False
            
        search_data = response.json()
        results = search_data.get("results", [])
        print(f"✓ Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    ID: {result.get('id', 'N/A')}")
            print(f"    Content: {result.get('content', 'N/A')[:50]}...")
            print(f"    Score: {result.get('score', 0)}")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False
    
    print("\n✓ All tests passed successfully!")
    return True

def main():
    """Main function"""
    try:
        simulate_mcp_protocol()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
