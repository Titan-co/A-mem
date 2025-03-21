"""
Simplified FastAPI server with Memory System but no memory evolution
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from memory_system import AgenticMemorySystem, MemoryNote
from config import settings
import traceback
import json

# Create FastAPI app
app = FastAPI(
    title="A-MEM Simple Server",
    description="A simplified A-MEM server for testing",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create memory system with evolution disabled
memory_system = None

@app.on_event("startup")
async def startup_event():
    # Initialize memory system
    global memory_system
    try:
        print("Initializing memory system...")
        print(f"Settings: MODEL_NAME={settings.MODEL_NAME}, "
              f"LLM_BACKEND={settings.LLM_BACKEND}, "
              f"LLM_MODEL={settings.LLM_MODEL}, "
              f"API_URL={settings.API_URL}")
        
        memory_system = AgenticMemorySystem(
            model_name=settings.MODEL_NAME,
            llm_backend=settings.LLM_BACKEND,
            llm_model=settings.LLM_MODEL,
            evo_threshold=settings.EVO_THRESHOLD,
            api_key=settings.API_KEY,
            api_base=settings.API_URL
        )
        
        # Override memory evolution method to disable it
        def mock_process_evolution(note):
            print("Memory evolution disabled")
            return False
        
        memory_system._process_memory_evolution = mock_process_evolution
        
        print("Memory system initialized successfully!")
    except Exception as e:
        print(f"Error initializing memory system: {e}")
        print(traceback.format_exc())

# Define API routes
@app.get("/")
async def root():
    return {
        "name": "A-MEM Simple Server",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/memories")
async def create_memory(request: dict):
    """Create a new memory"""
    if memory_system is None:
        raise HTTPException(status_code=500, detail="Memory system not initialized")
    
    try:
        content = request.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Create memory
        memory_id = memory_system.create(
            content=content,
            tags=request.get("tags", []),
            category=request.get("category", "General")
        )
        
        # Retrieve the created memory
        memory = memory_system.read(memory_id)
        
        # Convert to dictionary
        result = {
            "id": memory.id,
            "content": memory.content,
            "tags": memory.tags,
            "category": memory.category,
            "context": memory.context,
            "keywords": memory.keywords,
            "timestamp": memory.timestamp,
            "last_accessed": memory.last_accessed,
            "retrieval_count": memory.retrieval_count
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating memory: {str(e)}")

@app.get("/api/v1/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Retrieve a memory by ID"""
    if memory_system is None:
        raise HTTPException(status_code=500, detail="Memory system not initialized")
    
    memory = memory_system.read(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
    
    # Convert to dictionary
    result = {
        "id": memory.id,
        "content": memory.content,
        "tags": memory.tags,
        "category": memory.category,
        "context": memory.context,
        "keywords": memory.keywords,
        "timestamp": memory.timestamp,
        "last_accessed": memory.last_accessed,
        "retrieval_count": memory.retrieval_count
    }
    
    return result

@app.get("/api/v1/search")
async def search_memories(query: str, k: int = 5):
    """Search for memories"""
    if memory_system is None:
        raise HTTPException(status_code=500, detail="Memory system not initialized")
    
    results = memory_system.search(query, k)
    
    # Process results
    processed_results = []
    for result in results:
        processed_results.append({
            "id": result.get("id", ""),
            "content": result.get("content", ""),
            "context": result.get("context", ""),
            "keywords": result.get("keywords", []),
            "score": result.get("score", 0.0)
        })
    
    return {"results": processed_results}

@app.delete("/api/v1/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory by ID"""
    if memory_system is None:
        raise HTTPException(status_code=500, detail="Memory system not initialized")
    
    success = memory_system.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Memory with ID {memory_id} not found")
    
    return {"success": True, "message": f"Memory {memory_id} successfully deleted"}

if __name__ == "__main__":
    print("Starting A-MEM Simple Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
