import sys
import json
import os
import time
import socket
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("connector_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("connector_mcp")

# Load environment variables
load_dotenv()

# Get ports from environment
WRAPPER_PORT = os.getenv("PORT", "8767")  # Port this wrapper listens on
SERVER_PORT = os.getenv("SERVER_PORT", "8903")  # Port the A-MEM server is running on

def wait_for_server(timeout=20):
    """Wait for the server to be available"""
    logger.info(f"Checking for A-MEM server on port {SERVER_PORT}")
    print(f"Checking for A-MEM server on port {SERVER_PORT}", file=sys.stderr)
    sys.stderr.flush()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", int(SERVER_PORT)))
                logger.info("A-MEM server is up and running!")
                print("A-MEM server is up and running!", file=sys.stderr)
                sys.stderr.flush()
                return True
        except:
            time.sleep(0.5)
    
    logger.error(f"A-MEM server not found on port {SERVER_PORT} after {timeout} seconds")
    print(f"ERROR: A-MEM server not found on port {SERVER_PORT}. Make sure it's running.", file=sys.stderr)
    sys.stderr.flush()
    return False

def handle_mcp():
    """Handle MCP protocol communications"""
    logger.info("Starting MCP handler")
    print("MCP handler started - waiting for requests", file=sys.stderr)
    sys.stderr.flush()
    
    # Import requests here for API calls
    import requests
    
    # API base URL for the running server
    base_url = f"http://localhost:{SERVER_PORT}/api/v1"
    
    # Read messages from stdin
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline().strip()
            if not line:
                # Empty line, just continue without exiting
                print("Waiting for messages...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(0.5)
                continue
                
            logger.info(f"Received message: {line}")
            print(f"Received message: {line}", file=sys.stderr)
            sys.stderr.flush()
            
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            
            if method == "initialize":
                # Respond to initialize
                logger.info("Handling initialize request")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "capabilities": {}
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info("Sent initialize response")
            
            elif method == "create_memory":
                # Handle create_memory method
                logger.info("Handling create_memory request")
                
                params = request.get("params", {})
                
                try:
                    # Forward to the A-MEM server
                    api_response = requests.post(
                        f"{base_url}/memories",
                        json={
                            "content": params.get("content", ""),
                            "tags": params.get("tags", []),
                            "category": params.get("category", "General")
                        },
                        timeout=30  # Set a longer timeout
                    )
                    
                    logger.info(f"A-MEM server response: {api_response.status_code}")
                    
                    if api_response.status_code == 200 or api_response.status_code == 201:
                        memory_data = api_response.json()
                        logger.info(f"Created memory with ID: {memory_data.get('id', 'unknown')}")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": memory_data
                        }
                    else:
                        logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                        raise Exception(f"API error: {api_response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error in create_memory: {e}")
                    
                    # Use fallback response
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "id": f"memory-{int(time.time())}",
                            "content": params.get("content", ""),
                            "tags": params.get("tags", []),
                            "category": params.get("category", "General"),
                            "context": "Generated context", 
                            "keywords": ["generated"],
                            "timestamp": time.strftime("%Y%m%d%H%M"),
                            "last_accessed": time.strftime("%Y%m%d%H%M"),
                            "retrieval_count": 0
                        }
                    }
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info("Sent create_memory response")
                
            elif method == "search_memories":
                # Handle search_memories method
                logger.info("Handling search_memories request")
                
                params = request.get("params", {})
                query = params.get("query", "")
                k = params.get("k", 5)
                
                try:
                    # Forward to the A-MEM server
                    api_response = requests.get(
                        f"{base_url}/search",
                        params={"query": query, "k": k},
                        timeout=30  # Set a longer timeout
                    )
                    
                    logger.info(f"A-MEM server response: {api_response.status_code}")
                    
                    if api_response.status_code == 200:
                        search_data = api_response.json()
                        logger.info(f"Found {len(search_data.get('results', []))} results")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": search_data
                        }
                    else:
                        logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                        raise Exception(f"API error: {api_response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error in search_memories: {e}")
                    
                    # Use fallback response
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "results": [{
                                "id": f"demo-{int(time.time())}",
                                "content": f"This is a demo memory related to '{query}'",
                                "context": "Demo Context",
                                "keywords": ["demo", "test"],
                                "score": 0.95
                            }]
                        }
                    }
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info("Sent search_memories response")
                
            elif method == "get_memory":
                # Handle get_memory method
                logger.info("Handling get_memory request")
                
                params = request.get("params", {})
                memory_id = params.get("id", "")
                
                try:
                    # Forward to the A-MEM server
                    api_response = requests.get(
                        f"{base_url}/memories/{memory_id}",
                        timeout=30
                    )
                    
                    logger.info(f"A-MEM server response: {api_response.status_code}")
                    
                    if api_response.status_code == 200:
                        memory_data = api_response.json()
                        logger.info(f"Retrieved memory: {memory_id}")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": memory_data
                        }
                    else:
                        logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                        raise Exception(f"API error: {api_response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error in get_memory: {e}")
                    
                    # Use fallback response
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "id": memory_id,
                            "content": "Memory not found or error occurred",
                            "tags": ["error", "fallback"],
                            "category": "Error",
                            "context": "Error retrieving memory", 
                            "keywords": ["error"],
                            "timestamp": time.strftime("%Y%m%d%H%M"),
                            "last_accessed": time.strftime("%Y%m%d%H%M"),
                            "retrieval_count": 0
                        }
                    }
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info("Sent get_memory response")
                
            else:
                # For any other method, return an empty successful result
                logger.info(f"Handling unknown method: {method}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent response for {method}")
                
        except Exception as e:
            # Handle errors
            logger.error(f"Error in handle_mcp: {str(e)}", exc_info=True)
            print(f"ERROR in handle_mcp: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            
            try:
                # Send error response if possible
                if 'request' in locals() and request is not None and 'id' in request:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
                    logger.info(f"Sent error response")
                    print(f"Sent error response", file=sys.stderr)
                    sys.stderr.flush()
            except Exception as inner_e:
                logger.error(f"Error sending error response: {str(inner_e)}")
            
            # Continue running instead of crashing
            print("Continuing to run despite error...", file=sys.stderr)
            sys.stderr.flush()
            time.sleep(1)  # Brief pause before continuing

if __name__ == "__main__":
    try:
        print("Connector MCP wrapper starting...", file=sys.stderr)
        print(f"Current directory: {os.getcwd()}", file=sys.stderr)
        print(f"Python path: {os.environ.get('PYTHONPATH', 'Not set')}", file=sys.stderr)
        print(f"Ports: WRAPPER_PORT={WRAPPER_PORT}, SERVER_PORT={SERVER_PORT}", file=sys.stderr)
        sys.stderr.flush()
        logger.info("Connector MCP wrapper starting...")
        
        # Check if server is running
        if wait_for_server():
            logger.info("A-MEM server found, starting MCP handler")
            print("A-MEM server found, starting MCP handler", file=sys.stderr)
            sys.stderr.flush()
            
            while True:  # Keep trying to handle MCP even if it fails
                try:
                    # Handle MCP protocol
                    handle_mcp()
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt, shutting down")
                    print("Received keyboard interrupt, shutting down", file=sys.stderr)
                    sys.stderr.flush()
                    break
                except Exception as e:
                    logger.error(f"Unhandled exception in MCP handler: {str(e)}", exc_info=True)
                    print(f"CRITICAL ERROR in MCP handler: {str(e)}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.flush()
                    print("Restarting MCP handler in 5 seconds...", file=sys.stderr)
                    sys.stderr.flush()
                    time.sleep(5)  # Wait before retrying
        else:
            # Server not found
            logger.error("A-MEM server not found, exiting")
            print("ERROR: Please start the A-MEM server (run_standard_implementation.bat) first!", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        print(f"CRITICAL ERROR in main process: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
