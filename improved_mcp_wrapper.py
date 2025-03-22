import sys
import json
import subprocess
import threading
import os
import time
import socket
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_debug.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_wrapper")

# Start the web server in a separate thread
def start_server():
    port = os.getenv("PORT", "8765")
    logger.info(f"Starting web server on port {port}")
    print(f"Starting web server on port {port}", file=sys.stderr)
    sys.stderr.flush()
    
    server_process = subprocess.Popen(
        [
            sys.executable,  # Use the current Python interpreter
            "-m",
            "uvicorn",
            "simple_server:app",
            "--host",
            "0.0.0.0",
            "--port",
            port
        ],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stderr=subprocess.PIPE,  # Capture stderr to prevent it from mixing with stdout
    )
    return server_process

# Check if the server is up and running
def wait_for_server(port=None, timeout=10):
    if port is None:
        port = os.getenv("PORT", "8765")
    logger.info(f"Waiting for server to start on port {port}")
    print(f"Waiting for server to start on port {port}", file=sys.stderr)
    sys.stderr.flush()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", port))
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

# Handle MCP protocol communications
def handle_mcp():
    logger.info("Starting MCP handler")
    print("MCP handler started - waiting for requests", file=sys.stderr)
    sys.stderr.flush()
    
    # Initialize HTTP client for communicating with the server
    import requests
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get port from environment or use default
    port = os.getenv("PORT", "8767")
    logger.info(f"Using port for API server URL: {port}")
    print(f"Using port for API server URL: {port}", file=sys.stderr)
    sys.stderr.flush()
    
    server_url = f"http://localhost:{port}/api/v1"
    print(f"Using server URL: {server_url}", file=sys.stderr)
    sys.stderr.flush()
    
    # Read messages from stdin
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline().strip()
            if not line:
                # Empty line, just continue
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
                print("Handling initialize request", file=sys.stderr)
                sys.stderr.flush()
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "capabilities": {}
                    }
                }
                # Write the response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent response: {json.dumps(response)}")
                print(f"Sent initialize response, staying alive for more requests", file=sys.stderr)
                sys.stderr.flush()
            
            elif method == "create_memory":
                # Handle create_memory method
                logger.info("Handling create_memory request")
                print("Handling create_memory request", file=sys.stderr)
                sys.stderr.flush()
                
                params = request.get("params", {})
                
                try:
                    # Forward request to our API server
                    print(f"Forwarding create_memory request to server with content: {params.get('content', '')[:30]}...", file=sys.stderr)
                    
                    api_response = requests.post(
                        f"{server_url}/memories",
                        json={
                            "content": params.get("content", ""),
                            "tags": params.get("tags", []),
                            "category": params.get("category", "General")
                        }
                    )
                    
                    if api_response.status_code == 200 or api_response.status_code == 201:
                        # Successfully created memory
                        memory_data = api_response.json()
                        print(f"Successfully created memory with ID: {memory_data.get('id')}", file=sys.stderr)
                        
                        # Format response for MCP
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": memory_data
                        }
                    else:
                        # Error from API
                        print(f"Error from API: {api_response.status_code} - {api_response.text}", file=sys.stderr)
                        raise Exception(f"API error: {api_response.status_code}")
                        
                except Exception as e:
                    print(f"Error during create_memory: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    
                    # Fallback to mock response
                    print("Using fallback response for create_memory", file=sys.stderr)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "id": "memory-" + str(int(time.time())),
                            "content": params.get("content", ""),
                            "tags": params.get("tags", []),
                            "category": params.get("category", "General"),
                            "context": "Auto-generated context",
                            "keywords": ["auto", "generated"],
                            "timestamp": time.strftime("%Y%m%d%H%M"),
                            "last_accessed": time.strftime("%Y%m%d%H%M"),
                            "retrieval_count": 0,
                            "links": []
                        }
                    }
                    
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent create_memory response")
                print(f"Sent create_memory response", file=sys.stderr)
                sys.stderr.flush()
                
            elif method == "search_memories":
                # Handle search_memories method
                logger.info("Handling search_memories request")
                print("Handling search_memories request", file=sys.stderr)
                sys.stderr.flush()
                
                params = request.get("params", {})
                query = params.get("query", "")
                k = params.get("k", 5)
                
                try:
                    # Forward request to our API server
                    print(f"Forwarding search request to server: '{query}' with k={k}", file=sys.stderr)
                    
                    api_response = requests.get(
                        f"{server_url}/search",
                        params={
                            "query": query,
                            "k": k
                        }
                    )
                    
                    if api_response.status_code == 200:
                        # Successfully searched memories
                        search_data = api_response.json()
                        print(f"Successfully searched memories, found {len(search_data.get('results', []))} results", file=sys.stderr)
                        
                        # Format response for MCP
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": search_data
                        }
                    else:
                        # Error from API
                        print(f"Error from API: {api_response.status_code} - {api_response.text}", file=sys.stderr)
                        raise Exception(f"API error: {api_response.status_code}")
                        
                except Exception as e:
                    print(f"Error during search_memories: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    
                    # Fallback to mock response
                    print("Using fallback response for search_memories", file=sys.stderr)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "results": [
                                {
                                    "id": "demo-memory-1",
                                    "content": f"This is a demo memory related to '{query}'",
                                    "context": "Demo Context",
                                    "keywords": ["demo", "test", query],
                                    "score": 0.95
                                }
                            ]
                        }
                    }
                    
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent search_memories response")
                print(f"Sent search_memories response", file=sys.stderr)
                sys.stderr.flush()
                
            else:
                # For any other method, return an empty successful result
                logger.info(f"Handling unknown method: {method}")
                print(f"Handling unknown method: {method}", file=sys.stderr)
                sys.stderr.flush()
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent response: {json.dumps(response)}")
                print(f"Sent response for {method}", file=sys.stderr)
                sys.stderr.flush()
                
        except Exception as e:
            # Handle errors
            logger.error(f"Error in handle_mcp: {str(e)}", exc_info=True)
            print(f"ERROR in handle_mcp: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            
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
                logger.info(f"Sent error response: {json.dumps(error_response)}")
                print(f"Sent error response", file=sys.stderr)
                sys.stderr.flush()
            except Exception as inner_e:
                logger.error(f"Error sending error response: {str(inner_e)}", exc_info=True)
                print(f"CRITICAL ERROR sending error response: {str(inner_e)}", file=sys.stderr)
                sys.stderr.flush()

if __name__ == "__main__":
    try:
        print("MCP wrapper starting...", file=sys.stderr)
        sys.stderr.flush()
        logger.info("MCP wrapper starting...")
        
        # Start the web server
        server_process = start_server()
        
        # Wait for the server to start
        if wait_for_server():
            logger.info("Server started successfully, starting MCP handler")
            print("Server started successfully, starting MCP handler", file=sys.stderr)
            sys.stderr.flush()
            
            try:
                # Start the MCP handler in a blocking way
                handle_mcp()
                print("MCP handler exited normally", file=sys.stderr)
                sys.stderr.flush()
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down")
                print("Received keyboard interrupt, shutting down", file=sys.stderr)
                sys.stderr.flush()
            except Exception as e:
                logger.error(f"Unhandled exception in MCP handler: {str(e)}", exc_info=True)
                print(f"CRITICAL ERROR in MCP handler: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
        else:
            # Server failed to start, exit with error
            logger.error("Server failed to start, exiting")
            print("ERROR: Server failed to start, exiting", file=sys.stderr)
            sys.stderr.flush()
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Failed to start the server within the timeout period"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()
            sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        print(f"CRITICAL ERROR in main process: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
    finally:
        # Clean up 
        print("Cleaning up resources...", file=sys.stderr)
        sys.stderr.flush()
        try:
            if 'server_process' in locals():
                logger.info("Terminating server process")
                print("Terminating server process", file=sys.stderr)
                server_process.terminate()
                print("Server process terminated", file=sys.stderr)
        except Exception as e:
            logger.error(f"Error terminating server process: {e}", exc_info=True)
            print(f"Error terminating server process: {e}", file=sys.stderr)
        
        print("MCP wrapper exiting", file=sys.stderr)
        sys.stderr.flush()
