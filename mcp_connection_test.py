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
import traceback

def test_connection():
    """Test the ability to maintain a connection with the MCP protocol"""
    print("# A-MEM MCP Connection Test", file=sys.stderr)
    print("# =========================", file=sys.stderr)
    
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
    
    print(f"# Sending initialize message:", file=sys.stderr)
    sys.stdout.write(json.dumps(initialize_msg) + "\n")
    sys.stdout.flush()
    
    # Wait for response
    print("# Waiting for response...", file=sys.stderr)
    line = sys.stdin.readline().strip()
    print(f"# Received: {line}", file=sys.stderr)
    
    # Wait a bit
    print("# Waiting 3 seconds to test connection stability...", file=sys.stderr)
    time.sleep(3)
    
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
    
    print(f"# Sending create_memory message:", file=sys.stderr)
    sys.stdout.write(json.dumps(create_msg) + "\n")
    sys.stdout.flush()
    
    # Wait for response
    print("# Waiting for response...", file=sys.stderr)
    line = sys.stdin.readline().strip()
    print(f"# Received: {line}", file=sys.stderr)
    
    # Send a search memories message
    search_msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "search_memories",
        "params": {
            "query": "test connection",
            "k": 3
        }
    }
    
    print(f"# Sending search_memories message:", file=sys.stderr)
    sys.stdout.write(json.dumps(search_msg) + "\n")
    sys.stdout.flush()
    
    # Wait for response
    print("# Waiting for response...", file=sys.stderr)
    line = sys.stdin.readline().strip()
    print(f"# Received: {line}", file=sys.stderr)
    
    print("# Test completed successfully!", file=sys.stderr)
    return 0

if __name__ == "__main__":
    try:
        print("# Starting MCP connection test...", file=sys.stderr)
        sys.stderr.flush()
        result = test_connection()
        print("# MCP connection test completed with result code: {}".format(result), file=sys.stderr)
        sys.stderr.flush()
        sys.exit(result)
    except Exception as e:
        print(f"# ERROR: Test failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
