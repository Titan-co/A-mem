#!/usr/bin/env python
"""
Test script for MCP connection
This script tests the connection between Claude and the MCP server
"""
import json
import sys
import socket
import time
import os

def test_connection():
    """Test the ability to maintain a connection with the MCP protocol"""
    print("A-MEM MCP Connection Test")
    print("========================")
    
    # Send initialize message
    initialize_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"}
        }
    }
    
    print(f"Sending: {json.dumps(initialize_msg)}")
    sys.stdout.write(json.dumps(initialize_msg) + "\n")
    sys.stdout.flush()
    
    # Wait for response
    print("Waiting for response...")
    line = sys.stdin.readline().strip()
    print(f"Received: {line}")
    
    # Wait a bit
    print("Waiting 5 seconds to test connection stability...")
    time.sleep(5)
    
    # Send a create memory message
    create_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "create_memory",
        "params": {
            "content": "This is a test memory for debugging MCP connection",
            "tags": ["test", "debug", "mcp"],
            "category": "Testing"
        }
    }
    
    print(f"Sending: {json.dumps(create_msg)}")
    sys.stdout.write(json.dumps(create_msg) + "\n")
    sys.stdout.flush()
    
    # Wait for response
    print("Waiting for response...")
    line = sys.stdin.readline().strip()
    print(f"Received: {line}")
    
    print("Test completed successfully!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test_connection())
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
