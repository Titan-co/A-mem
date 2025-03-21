import sys
import json
import time
import os

def simulate_mcp_protocol():
    """Simulate the MCP protocol to test the server's response to MCP messages."""
    
    print("A-MEM MCP Protocol Tester")
    print("=========================")
    print("This script simulates MCP client-server communication.")
    print("The server should respond to JSON-RPC formatted messages.")
    
    # Test 1: Initialize
    print("\nTest 1: Initialize message")
    request = {
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "0.1.0"
            }
        },
        "jsonrpc": "2.0",
        "id": 1
    }
    
    print(f"Sending: {json.dumps(request)}")
    request_json = json.dumps(request) + "\n"
    sys.stdout.write(request_json)
    sys.stdout.flush()
    
    print("Waiting for response...")
    time.sleep(2)
    
    # Test 2: Create memory
    print("\nTest 2: Create memory")
    request = {
        "method": "create_memory",
        "params": {
            "content": f"Test memory created at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "tags": ["test", "mcp"],
            "category": "Testing"
        },
        "jsonrpc": "2.0",
        "id": 2
    }
    
    print(f"Sending: {json.dumps(request)}")
    request_json = json.dumps(request) + "\n"
    sys.stdout.write(request_json)
    sys.stdout.flush()
    
    print("Waiting for response...")
    time.sleep(2)
    
    # Test 3: Search memories
    print("\nTest 3: Search memories")
    request = {
        "method": "search_memories",
        "params": {
            "query": "test",
            "k": 5
        },
        "jsonrpc": "2.0",
        "id": 3
    }
    
    print(f"Sending: {json.dumps(request)}")
    request_json = json.dumps(request) + "\n"
    sys.stdout.write(request_json)
    sys.stdout.flush()
    
    print("Waiting for response...")
    time.sleep(2)
    
    print("\nMCP Protocol test complete")
    print("Check the server logs for responses")

if __name__ == "__main__":
    # Check if running in the correct environment
    print("Checking environment...")
    if "CLAUDE_MCP_SERVER" in os.environ:
        print("Running in Claude MCP environment, proceeding with test")
        simulate_mcp_protocol()
    else:
        print("Not running in Claude MCP environment")
        print("This script is designed to be executed by the Claude Desktop MCP interface")
        print("It won't work correctly in a regular terminal")
        print("")
        print("To test manually:")
        print("1. Start the MCP server with Claude Desktop")
        print("2. The following JSON messages should be sent to test the protocol:")
        
        # Initialize message
        init_msg = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "0.1.0"
                }
            },
            "jsonrpc": "2.0",
            "id": 1
        }
        print("\nInitialize message:")
        print(json.dumps(init_msg, indent=2))
        
        # Create memory message
        create_msg = {
            "method": "create_memory",
            "params": {
                "content": "Test memory content",
                "tags": ["test", "mcp"],
                "category": "Testing"
            },
            "jsonrpc": "2.0",
            "id": 2
        }
        print("\nCreate memory message:")
        print(json.dumps(create_msg, indent=2))
        
        # Search memories message
        search_msg = {
            "method": "search_memories",
            "params": {
                "query": "test",
                "k": 5
            },
            "jsonrpc": "2.0",
            "id": 3
        }
        print("\nSearch memories message:")
        print(json.dumps(search_msg, indent=2))
