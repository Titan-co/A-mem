import requests
import json

class AMEMClient:
    """Client for interacting with the A-MEM MCP Server"""
    
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        """Initialize the client with the server base URL"""
        self.base_url = base_url
    
    def create_memory(self, content, tags=None, category=None, timestamp=None):
        """Create a new memory"""
        endpoint = f"{self.base_url}/memories"
        
        payload = {"content": content}
        if tags:
            payload["tags"] = tags
        if category:
            payload["category"] = category
        if timestamp:
            payload["timestamp"] = timestamp
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_memory(self, memory_id):
        """Retrieve a memory by ID"""
        endpoint = f"{self.base_url}/memories/{memory_id}"
        
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    def update_memory(self, memory_id, **kwargs):
        """Update an existing memory"""
        endpoint = f"{self.base_url}/memories/{memory_id}"
        
        response = requests.put(endpoint, json=kwargs)
        response.raise_for_status()
        return response.json()
    
    def delete_memory(self, memory_id):
        """Delete a memory by ID"""
        endpoint = f"{self.base_url}/memories/{memory_id}"
        
        response = requests.delete(endpoint)
        response.raise_for_status()
        return response.json()
    
    def search_memories(self, query, k=5):
        """Search for memories"""
        endpoint = f"{self.base_url}/search"
        
        params = {
            "query": query,
            "k": k
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

def main():
    """Example usage of the A-MEM client"""
    client = AMEMClient()
    
    try:
        # Create several memories
        print("Creating memories...")
        memory1 = client.create_memory(
            content="Large Language Models require sophisticated memory systems for effective operation.",
            tags=["llm", "memory", "ai"],
            category="Research"
        )
        print(f"Created memory with ID: {memory1['id']}")
        
        memory2 = client.create_memory(
            content="Agentic memory systems allow for dynamic organization and evolution of knowledge.",
            tags=["memory", "agent", "organization"],
            category="Research"
        )
        print(f"Created memory with ID: {memory2['id']}")
        
        memory3 = client.create_memory(
            content="The Zettelkasten method is a knowledge management system featuring atomic notes and flexible linking.",
            tags=["zettelkasten", "knowledge", "organization"],
            category="Methodology"
        )
        print(f"Created memory with ID: {memory3['id']}")
        
        # Retrieve a memory
        print("\nRetrieving memory...")
        memory = client.get_memory(memory1['id'])
        print(json.dumps(memory, indent=2))
        
        # Update a memory
        print("\nUpdating memory...")
        updated_memory = client.update_memory(
            memory1['id'],
            content="Large Language Models require sophisticated and dynamic memory systems for effective operation.",
            tags=["llm", "memory", "ai", "dynamic"]
        )
        print(json.dumps(updated_memory, indent=2))
        
        # Search for memories
        print("\nSearching memories...")
        search_results = client.search_memories("memory systems", k=3)
        for i, result in enumerate(search_results['results']):
            print(f"\nResult {i+1}:")
            print(f"ID: {result['id']}")
            print(f"Content: {result['content']}")
            print(f"Score: {result['score']}")
        
        # Delete a memory
        print("\nDeleting memory...")
        delete_result = client.delete_memory(memory3['id'])
        print(json.dumps(delete_result, indent=2))
        
        # Verify deletion by searching again
        print("\nVerifying deletion through search...")
        search_results = client.search_memories("zettelkasten", k=1)
        print(f"Found {len(search_results['results'])} results")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("A-MEM MCP Client Example")
    print("------------------------")
    print("Make sure the A-MEM MCP Server is running before executing this script!")
    print("------------------------\n")
    
    main()
