from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import time
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Get port from environment or use default
port = int(os.getenv("PORT", 8767))

# Create FastAPI app
app = FastAPI(
    title="A-MEM Fallback Server",
    description="A simplified A-MEM server for testing",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
memories = {}

@app.get("/")
async def root():
    return {"status": "A-MEM Fallback Server is running!", "port": port}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/search")
async def search_memories(query: str, k: int = 5):
    """Search for memories"""
    print(f"Searching for: '{query}' with k={k}", file=sys.stderr)
    
    # Simple search implementation
    results = []
    
    for memory_id, memory in memories.items():
        if query.lower() in memory["content"].lower():
            results.append({
                "id": memory_id,
                "content": memory["content"],
                "context": memory.get("context", "General"),
                "keywords": memory.get("keywords", ["auto-generated"]),
                "score": 0.95  # Mock score
            })
    
    # Limit results
    results = results[:k]
    
    # If no results, return a mock result
    if not results:
        results.append({
            "id": "demo-1",
            "content": f"This is a demo memory related to '{query}'",
            "context": "Demo Context",
            "keywords": ["demo", "test"],
            "score": 0.9
        })
    
    return {"results": results}

@app.post("/api/v1/memories")
async def create_memory(request: Request):
    """Create a memory"""
    body = await request.json()
    
    # Generate ID
    memory_id = str(uuid.uuid4())
    
    # Store memory
    memory = {
        "id": memory_id,
        "content": body.get("content", ""),
        "tags": body.get("tags", []),
        "category": body.get("category", "General"),
        "context": "Auto-generated context",
        "keywords": ["auto-generated"],
        "timestamp": time.strftime("%Y%m%d%H%M"),
        "last_accessed": time.strftime("%Y%m%d%H%M"),
        "retrieval_count": 0
    }
    
    memories[memory_id] = memory
    
    print(f"Created memory with ID: {memory_id}", file=sys.stderr)
    return memory

@app.get("/api/v1/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get a memory by ID"""
    if memory_id in memories:
        # Update retrieval count
        memories[memory_id]["retrieval_count"] += 1
        memories[memory_id]["last_accessed"] = time.strftime("%Y%m%d%H%M")
        return memories[memory_id]
    
    # Return mock memory if not found
    return {
        "id": memory_id,
        "content": f"This is a demo memory with ID {memory_id}",
        "tags": ["demo", "test"],
        "category": "General",
        "context": "Demo Context",
        "keywords": ["demo", "test"],
        "timestamp": time.strftime("%Y%m%d%H%M"),
        "last_accessed": time.strftime("%Y%m%d%H%M"),
        "retrieval_count": 1
    }

@app.delete("/api/v1/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory"""
    if memory_id in memories:
        del memories[memory_id]
    
    return {"success": True, "message": f"Memory {memory_id} deleted or not found"}

if __name__ == "__main__":
    print(f"Starting fallback server on port {port}...", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=port)
