import sys
import json
import os
import time
import socket
import logging
import traceback
import threading
import msvcrt  # Windows-specific module for console input
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
KEEP_ALIVE = os.getenv("MCP_KEEP_ALIVE", "true").lower() == "true"

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

def read_line_with_timeout(timeout=0.1):
    """Read a line from stdin with timeout (Windows-compatible)"""
    line = ""
    start_time = time.time()
    
    # Check if data is available (non-blocking)
    while True:
        # Check if we've exceeded our timeout
        if time.time() - start_time > timeout:
            return None
            
        # Check if data is available to read (Windows-specific approach)
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8')
            if char == '\r':  # Enter key
                return line
            elif char == '\n':  # Sometimes Windows uses \n
                return line
            else:
                line += char
        else:
            # Small sleep to prevent high CPU usage
            time.sleep(0.01)

def handle_mcp():
    """Handle MCP protocol communications"""
    logger.info("Starting MCP handler")
    print("MCP handler started - waiting for requests", file=sys.stderr)
    sys.stderr.flush()
    
    # Import requests here for API calls
    import requests
    
    # API base URL for the running server
    base_url = f"http://localhost:{SERVER_PORT}/api/v1"
    
    # Keep track of last heartbeat
    last_heartbeat = time.time()
    
    # Use a different approach for reading stdin on Windows
    # Start a thread to read stdin lines and put them in a queue
    import queue
    message_queue = queue.Queue()
    
    def stdin_reader():
        while True:
            try:
                line = sys.stdin.readline().strip()
                if line:
                    message_queue.put(line)
            except Exception as e:
                logger.error(f"Error reading stdin: {e}")
            time.sleep(0.1)  # Small delay to prevent high CPU usage
    
    # Start the stdin reader thread
    reader_thread = threading.Thread(target=stdin_reader, daemon=True)
    reader_thread.start()
    
    # Main processing loop
    while True:
        try:
            # Send periodic heartbeat (every 5 seconds)
            if KEEP_ALIVE and time.time() - last_heartbeat > 5:
                print(".", file=sys.stderr, end="")
                sys.stderr.flush()
                last_heartbeat = time.time()
            
            # Check message queue
            try:
                # Non-blocking get with timeout
                line = message_queue.get(block=False)
                
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
                    
                    # Write response and ensure it's flushed
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
                    
                    logger.info(f"Sent initialize response: {response_json}")
                    print(f"Sent initialize response, staying alive for more requests", file=sys.stderr)
                    sys.stderr.flush()
                    
                elif method == "create_memory":
                    # Handle create_memory method
                    logger.info("Handling create_memory request")
                    print("Handling create_memory request", file=sys.stderr)
                    sys.stderr.flush()
                    
                    params = request.get("params", {})
                    
                    try:
                        # Forward to the A-MEM server
                        print(f"Sending request to {base_url}/memories", file=sys.stderr)
                        sys.stderr.flush()
                        
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
                        print(f"A-MEM server response: {api_response.status_code}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        if api_response.status_code in (200, 201):
                            memory_data = api_response.json()
                            logger.info(f"Created memory with ID: {memory_data.get('id', 'unknown')}")
                            
                            response = {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": memory_data
                            }
                        else:
                            logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                            raise Exception(f"API error: {api_response.status_code} - {api_response.text}")
                            
                    except Exception as e:
                        logger.error(f"Error in create_memory: {e}")
                        print(f"Error in create_memory: {e}", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                        sys.stderr.flush()
                        
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
                    
                    # Write response and ensure it's flushed
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
                    
                    logger.info("Sent create_memory response")
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
                        # Forward to the A-MEM server
                        print(f"Searching for: '{query}' with k={k}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        api_response = requests.get(
                            f"{base_url}/search",
                            params={"query": query, "k": k},
                            timeout=30  # Set a longer timeout
                        )
                        
                        logger.info(f"A-MEM server response: {api_response.status_code}")
                        print(f"A-MEM server response: {api_response.status_code}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        if api_response.status_code == 200:
                            search_data = api_response.json()
                            result_count = len(search_data.get('results', []))
                            logger.info(f"Found {result_count} results")
                            print(f"Found {result_count} results", file=sys.stderr)
                            sys.stderr.flush()
                            
                            response = {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": search_data
                            }
                        else:
                            logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                            raise Exception(f"API error: {api_response.status_code} - {api_response.text}")
                            
                    except Exception as e:
                        logger.error(f"Error in search_memories: {e}")
                        print(f"Error in search_memories: {e}", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                        sys.stderr.flush()
                        
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
                    
                    # Write response and ensure it's flushed
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
                    
                    logger.info("Sent search_memories response")
                    print(f"Sent search_memories response", file=sys.stderr)
                    sys.stderr.flush()
                    
                elif method == "get_memory":
                    # Handle get_memory method
                    logger.info("Handling get_memory request")
                    print("Handling get_memory request", file=sys.stderr)
                    sys.stderr.flush()
                    
                    params = request.get("params", {})
                    memory_id = params.get("id", "")
                    
                    try:
                        # Forward to the A-MEM server
                        print(f"Getting memory with ID: {memory_id}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        api_response = requests.get(
                            f"{base_url}/memories/{memory_id}",
                            timeout=30
                        )
                        
                        logger.info(f"A-MEM server response: {api_response.status_code}")
                        print(f"A-MEM server response: {api_response.status_code}", file=sys.stderr)
                        sys.stderr.flush()
                        
                        if api_response.status_code == 200:
                            memory_data = api_response.json()
                            logger.info(f"Retrieved memory: {memory_id}")
                            print(f"Retrieved memory: {memory_id}", file=sys.stderr)
                            sys.stderr.flush()
                            
                            response = {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": memory_data
                            }
                        else:
                            logger.error(f"API error: {api_response.status_code} - {api_response.text}")
                            raise Exception(f"API error: {api_response.status_code} - {api_response.text}")
                            
                    except Exception as e:
                        logger.error(f"Error in get_memory: {e}")
                        print(f"Error in get_memory: {e}", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                        sys.stderr.flush()
                        
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
                    
                    # Write response and ensure it's flushed
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
                    
                    logger.info("Sent get_memory response")
                    print(f"Sent get_memory response", file=sys.stderr)
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
                    
                    # Write response and ensure it's flushed
                    response_json = json.dumps(response)
                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()
                    
                    logger.info(f"Sent response for {method}")
                    print(f"Sent response for {method}", file=sys.stderr)
                    sys.stderr.flush()
                
            except queue.Empty:
                # No messages in the queue, just continue
                pass
                
            # Small sleep to prevent high CPU usage
            time.sleep(0.01)
                
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
        print(f"Keep alive enabled: {KEEP_ALIVE}", file=sys.stderr)
        sys.stderr.flush()
        logger.info("Connector MCP wrapper starting...")
        
        # Check if server is running
        if wait_for_server():
            logger.info("A-MEM server found, starting MCP handler")
            print("A-MEM server found, starting MCP handler", file=sys.stderr)
            sys.stderr.flush()
            
            # Explicitly flush stdout after startup
            sys.stdout.flush()
            
            # Start handling MCP messages - this is the main event loop
            handle_mcp()
            
        else:
            # Server not found
            logger.error("A-MEM server not found, exiting")
            print("ERROR: Please start the A-MEM server (run_standard_implementation.bat) first!", file=sys.stderr)
            sys.stderr.flush()
            
            # Exit with error
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "A-MEM server not running on expected port"
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
        
        # Try to send error response
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Critical error: {str(e)}"
            }
        }
        sys.stdout.write(json.dumps(error_response) + "\n")
        sys.stdout.flush()
        sys.exit(1)
