import sys
import json
import subprocess
import threading
import os
import time
import socket
import logging

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
    logger.info("Starting web server on port 8765")
    server_process = subprocess.Popen(
        [
            "C:\\Users\\zsun2\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
            "-m",
            "uvicorn",
            "simple_server:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8765"
        ],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stderr=subprocess.PIPE,  # Capture stderr to prevent it from mixing with stdout
    )
    return server_process

# Check if the server is up and running
def wait_for_server(port=8765, timeout=10):
    logger.info(f"Waiting for server to start on port {port}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", port))
                logger.info("Server is up and running!")
                return True
        except:
            time.sleep(0.5)
    logger.error(f"Server failed to start within {timeout} seconds")
    return False

# Handle MCP protocol communications
def handle_mcp():
    logger.info("Starting MCP handler")
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
                # Write the response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                logger.info(f"Sent response: {json.dumps(response)}")
            
            elif method == "create_memory":
                # Handle create_memory method
                logger.info("Handling create_memory request")
                params = request.get("params", {})
                
                # Create a simple response
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
                logger.info(f"Sent response: {json.dumps(response)}")
                
            elif method == "search_memories":
                # Handle search_memories method
                logger.info("Handling search_memories request")
                params = request.get("params", {})
                query = params.get("query", "")
                k = params.get("k", 5)
                
                # Create a simple response
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
                logger.info(f"Sent response: {json.dumps(response)}")
                
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
                logger.info(f"Sent response: {json.dumps(response)}")
                
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
                logger.info(f"Sent error response: {json.dumps(error_response)}")
            except Exception as inner_e:
                logger.error(f"Error sending error response: {str(inner_e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("MCP wrapper starting...")
    # Start the web server
    server_process = start_server()
    
    # Wait for the server to start
    if wait_for_server():
        logger.info("Server started successfully, starting MCP handler")
        try:
            # Start the MCP handler in a blocking way
            handle_mcp()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logger.error(f"Unhandled exception in main: {str(e)}", exc_info=True)
        finally:
            # Clean up
            logger.info("Terminating server process")
            try:
                server_process.terminate()
            except Exception as e:
                logger.error(f"Error terminating server process: {str(e)}", exc_info=True)
    else:
        # Server failed to start, exit with error
        logger.error("Server failed to start, exiting")
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
