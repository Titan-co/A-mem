#!/usr/bin/env python
"""
Simple diagnostic test script for A-MEM server
This will perform a very basic test of the server's API endpoints
"""
import requests
import sys
import time
import traceback
import json

def test_server(base_url="http://localhost:8903"):
    """Test basic API functionality"""
    print("=" * 60)
    print("A-MEM Server Basic Test")
    print("=" * 60)
    print(f"Testing server at {base_url}")
    
    try:
        # Test 1: Health check
        print("\nTest 1: Health check")
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                print("✓ Health check passed")
            else:
                print(f"✗ Health check failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check error: {e}")
            return False
        
        # Test 2: Create memory with minimal content
        print("\nTest 2: Create a minimal memory")
        try:
            minimal_content = "Test memory"
            response = requests.post(
                f"{base_url}/api/v1/memories",
                json={"content": minimal_content},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")  # Limit response length
            
            if response.status_code in (200, 201):
                try:
                    memory_data = response.json()
                    memory_id = memory_data.get("id")
                    print(f"✓ Created memory with ID: {memory_id}")
                except Exception as parse_error:
                    print(f"✗ Could not parse response JSON: {parse_error}")
                    return False
            else:
                print(f"✗ Create memory failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Create memory error: {e}")
            traceback.print_exc()
            return False
        
        # Test 3: Search for the created memory
        print("\nTest 3: Search for memories")
        try:
            response = requests.get(
                f"{base_url}/api/v1/search",
                params={"query": "Test", "k": 5},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")  # Limit response length
            
            if response.status_code == 200:
                try:
                    results = response.json().get("results", [])
                    print(f"✓ Found {len(results)} results")
                except Exception as parse_error:
                    print(f"✗ Could not parse search results: {parse_error}")
                    return False
            else:
                print(f"✗ Search failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Search error: {e}")
            traceback.print_exc()
            return False
        
        print("\n✓ All tests passed!")
        return True
    except Exception as e:
        print(f"✗ Unhandled error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Allow custom URL from command line
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8903"
    success = test_server(url)
    sys.exit(0 if success else 1)
