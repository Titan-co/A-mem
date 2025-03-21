import os
import json
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Example in-memory database for testing
memories_db = {}

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
api_router = FastAPI()

@app.get("/")
async def root():
    return {"status": "A-MEM Server is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/mcp-schema")
async def get_schema():
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "mcp_schema.json")
        with open(schema_path, "r") as f:
            schema = json.load(f)
        return JSONResponse(content=schema)
    except Exception as e:
        return {"error": str(e)}

# Include API router
app.mount("/api/v1", api_router)

@api_router.get("/search")
async def search_memories(query: str, k: int = 5):
    """Search for memories (simplified version)"""
    # Basic search implementation
    results = []
    
    # Check if we have any memories
    if not memories_db:
        # Return a demo result if no memories exist
        return {
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
    
    # Simple search based on content contains
    for memory_id, memory in memories_db.items():
        if query.lower() in memory["content"].lower():
            # Calculate a simple relevance score
            score = 0.5 + (memory["content"].lower().count(query.lower()) * 0.1)
            
            # Add to results
            results.append({
                "id": memory_id,
                "content": memory["content"],
                "context": memory["context"],
                "keywords": memory["keywords"],
                "score": min(0.99, score)  # Cap at 0.99
            })
    
    # Sort by score
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Limit results
    results = results[:k]
    
    # If no results, add a demo result
    if not results:
        results.append({
            "id": "demo-memory-1",
            "content": f"No matches found for '{query}'. This is a demo result.",
            "context": "Demo Context",
            "keywords": ["demo", "no-match"],
            "score": 0.1
        })
    
    return {"results": results}

@api_router.post("/memories")
async def create_memory(request: Request):
    """Create a memory (simplified version)"""
    body = await request.json()
    content = body.get("content", "")
    
    # Generate a unique ID
    import time
    import uuid
    memory_id = str(uuid.uuid4())
    
    # Create a new memory
    new_memory = {
        "id": memory_id,
        "content": content,
        "tags": body.get("tags", []),
        "category": body.get("category", "General"),
        "context": "Auto-generated context",
        "keywords": ["auto", "generated"],
        "timestamp": time.strftime("%Y%m%d%H%M"),
        "last_accessed": time.strftime("%Y%m%d%H%M"),
        "retrieval_count": 0,
        "links": []
    }
    
    # Store in the database
    memories_db[memory_id] = new_memory
    
    return new_memory

@api_router.get("/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get a memory by ID (simplified version)"""
    if memory_id in memories_db:
        # Update access count and timestamp
        import time
        memories_db[memory_id]["retrieval_count"] += 1
        memories_db[memory_id]["last_accessed"] = time.strftime("%Y%m%d%H%M")
        return memories_db[memory_id]
    
    # If not found, return a demo memory
    return {
        "id": memory_id,
        "content": f"This is the content of memory {memory_id}",
        "tags": ["demo", "test"],
        "category": "General",
        "context": "Auto-generated context",
        "keywords": ["auto", "generated"],
        "timestamp": "202503211200",
        "last_accessed": "202503211200",
        "retrieval_count": 1,
        "links": []
    }

@api_router.put("/memories/{memory_id}")
async def update_memory(memory_id: str, request: Request):
    """Update a memory (simplified version)"""
    body = await request.json()
    
    if memory_id in memories_db:
        # Update fields that are provided
        memory = memories_db[memory_id]
        for key, value in body.items():
            if key in memory:
                memory[key] = value
        
        # Update access timestamp
        import time
        memory["last_accessed"] = time.strftime("%Y%m%d%H%M")
        memory["retrieval_count"] += 1
        
        return memory
    
    # If not found, create a new memory with this ID
    import time
    new_memory = {
        "id": memory_id,
        "content": body.get("content", f"Updated content for memory {memory_id}"),
        "tags": body.get("tags", ["updated", "demo"]),
        "category": body.get("category", "General"),
        "context": body.get("context", "Updated context"),
        "keywords": body.get("keywords", ["updated", "generated"]),
        "timestamp": time.strftime("%Y%m%d%H%M"),
        "last_accessed": time.strftime("%Y%m%d%H%M"),
        "retrieval_count": 1,
        "links": []
    }
    
    memories_db[memory_id] = new_memory
    return new_memory

@api_router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory (simplified version)"""
    if memory_id in memories_db:
        del memories_db[memory_id]
    return {
        "success": True,
        "message": f"Memory {memory_id} successfully deleted"
    }

if __name__ == "__main__":
    import sys
    import json
    # Print JSON to stdout for MCP
    print(json.dumps({"jsonrpc": "2.0", "id": 0, "result": {"capabilities": {}}}))
    sys.stdout.flush()
    # Start the server
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8765, log_level="debug")
