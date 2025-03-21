import requests
import json
import time

def test_api(base_url="http://localhost:8000/api/v1"):
    """Test the A-MEM API endpoints"""
    print("Testing A-MEM API...")
    
    # Test 1: Create a memory
    print("\n1. Testing memory creation...")
    try:
        response = requests.post(
            f"{base_url}/memories",
            json={
                "content": f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "tags": ["test", "api"],
                "category": "Testing"
            }
        )
        response.raise_for_status()
        memory_data = response.json()
        memory_id = memory_data.get("id")
        print(f"SUCCESS: Created memory with ID: {memory_id}")
        print(f"Memory details: {json.dumps(memory_data, indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")
        memory_id = None
    
    # If memory creation failed, we can't continue with other tests
    if not memory_id:
        print("Memory creation failed, cannot continue with other tests.")
        return
    
    # Test 2: Retrieve a memory
    print("\n2. Testing memory retrieval...")
    try:
        response = requests.get(f"{base_url}/memories/{memory_id}")
        response.raise_for_status()
        memory_data = response.json()
        print(f"SUCCESS: Retrieved memory with ID: {memory_id}")
        print(f"Memory details: {json.dumps(memory_data, indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: Update a memory
    print("\n3. Testing memory update...")
    try:
        response = requests.put(
            f"{base_url}/memories/{memory_id}",
            json={
                "content": f"Updated test memory at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "tags": ["test", "api", "updated"]
            }
        )
        response.raise_for_status()
        memory_data = response.json()
        print(f"SUCCESS: Updated memory with ID: {memory_id}")
        print(f"Memory details: {json.dumps(memory_data, indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 4: Search for memories
    print("\n4. Testing memory search...")
    try:
        response = requests.get(f"{base_url}/search?query=test&k=5")
        response.raise_for_status()
        search_results = response.json()
        print(f"SUCCESS: Found {len(search_results.get('results', []))} search results")
        for i, result in enumerate(search_results.get("results", []), 1):
            print(f"Result {i}:")
            print(f"ID: {result.get('id')}")
            print(f"Content: {result.get('content')}")
            print(f"Score: {result.get('score')}")
            print("---")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 5: Delete a memory
    print("\n5. Testing memory deletion...")
    try:
        response = requests.delete(f"{base_url}/memories/{memory_id}")
        response.raise_for_status()
        delete_result = response.json()
        print(f"SUCCESS: Deleted memory with ID: {memory_id}")
        print(f"Deletion result: {json.dumps(delete_result, indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    print("=" * 50)
    print("A-MEM API Test Script")
    print("=" * 50)
    print("Make sure the A-MEM server is running before executing this script!")
    print("Default URL: http://localhost:8000/api/v1")
    print("=" * 50)
    
    # Get custom URL if provided
    custom_url = input("Enter custom base URL or press Enter for default: ").strip()
    base_url = custom_url if custom_url else "http://localhost:8000/api/v1"
    
    test_api(base_url)
