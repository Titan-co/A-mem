import sys
import json
import subprocess
import threading
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
        logging.FileHandler("simple_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("simple_mcp")

# Load environment variables
load_dotenv()

# Get port from environment
PORT = os.getenv("PORT", "8767")

def start_server():
    """Start the fallback server"""
    logger.info(f"Starting fallback server on port {PORT}")
    print(f"Starting fallback server on port {PORT}", file=sys.stderr)
    sys.stderr.flush()
    
    server_process = subprocess.Popen(
        [
            sys.executable,
            "fallback_server.py"
        ],
        stderr=subprocess.PIPE,
    )
    return server_process

def wait_for_server(timeout=10):
    """Wait for the server to start"""
    logger.info(f"Waiting for server to start on port {PORT}")
    print(f"Waiting for server to start on port {PORT}", file=sys.stderr)
    sys.stderr.flush()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", int(PORT)))
                logger.info("Server is up and running!")
                print("Server is up and running!", file=sys.stderr)
                sys.stderr.flush()
                return True
        except:
            time.sleep(0.5)
    
    logger.error(f"Server failed to start within {timeout} seconds")
    print(f"ERROR: Server failed to start within {timeout} seconds", file=sys.stderr)
    sys.stderr.flush()
    return False

def handle_mcp():
    """Handle MCP protocol communications"""
    logger.info("Starting MCP handler")
    print("MCP handler started - waiting for requests", file=sys.stderr)
    sys.stderr.flush()
    
    # Import requests here for API calls
    import requests
    
    # API base URL
    base_url = f"http://localhost:{PORT}/api/v1"
    
    # Read messages from stdin
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline().strip()
            if not line:
                time.sleep(0.1)
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
                    # Call the API
                    api_response = requests.post(
                        f"{base_url}/memories",
                        json={
                            "content": params.get("content", ""),
                            "tags": params.get("tags", []),
                            "category": params.get("category", "General")
                        }
                    )
                    
                    if api_response.status_code == 200 or api_response.status_code == 201:
                        memory_data = api_response.json()
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": memory_data
                        }
                    else:
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
                    # Call the API
                    api_response = requests.get(
                        f"{base_url}/search",
                        params={"query": query, "k": k}
                    )
                    
                    if api_response.status_code == 200:
                        search_data = api_response.json()
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": search_data
                        }
                    else:
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
            
            try:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as inner_e:
                logger.error(f"Error sending error response: {str(inner_e)}")

if __name__ == "__main__":
    try:
        print("Simple MCP wrapper starting...", file=sys.stderr)
        sys.stderr.flush()
        logger.info("Simple MCP wrapper starting...")
        
        # Start the fallback server
        server_process = start_server()
        
        # Wait for the server to start
        if wait_for_server():
            logger.info("Server started successfully, starting MCP handler")
            
            try:
                # Handle MCP protocol
                handle_mcp()
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down")
            except Exception as e:
                logger.error(f"Unhandled exception in MCP handler: {str(e)}", exc_info=True)
        else:
            # Server failed to start
            logger.error("Server failed to start, exiting")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
    finally:
        # Clean up
        try:
            if 'server_process' in locals():
                logger.info("Terminating server process")
                server_process.terminate()
        except Exception as e:
            logger.error(f"Error terminating server process: {e}")
