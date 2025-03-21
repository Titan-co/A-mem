"""
A-MEM MCP Server with robust error handling for API variations
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import traceback
from config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import memory system with error handling
try:
    from memory_system import AgenticMemorySystem, MemoryNote
    
    # Create custom memory system with error handling
    memory_system = None
    
    def init_memory_system():
        global memory_system
        try:
            logger.info("Initializing memory system...")
            logger.info(f"Settings: MODEL_NAME={settings.MODEL_NAME}, "
                        f"LLM_BACKEND={settings.LLM_BACKEND}, "
                        f"LLM_MODEL={settings.LLM_MODEL}")
            
            memory_system = AgenticMemorySystem(
                model_name=settings.MODEL_NAME,
                llm_backend=settings.LLM_BACKEND,
                llm_model=settings.LLM_MODEL,
                evo_threshold=settings.EVO_THRESHOLD,
                api_key=settings.API_KEY,
                api_base=settings.API_URL
            )
            
            # Override analyze_content to make it more robust
            original_analyze = memory_system.analyze_content
            
            def robust_analyze(content):
                try:
                    return original_analyze(content)
                except Exception as e:
                    logger.error(f"Error in content analysis, using fallback: {e}")
                    # Provide a simple fallback when analysis fails
                    return {
                        "keywords": ["auto-generated"],
                        "context": "General", 
                        "tags": ["auto-tagged"]
                    }
            
            # Replace with robust version
            memory_system.analyze_content = robust_analyze
            
            # Override evolution to be more robust
            original_evolution = memory_system._process_memory_evolution
            
            def robust_evolution(note):
                try:
                    return original_evolution(note)
                except Exception as e:
                    logger.error(f"Error in memory evolution, disabling: {e}")
                    return False
                
            # Replace with robust version
            memory_system._process_memory_evolution = robust_evolution
            
            logger.info("Memory system initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"Error initializing memory system: {e}")
            logger.error(traceback.format_exc())
            return False
except Exception as e:
    logger.error(f"Error importing memory_system: {e}")
    logger.error(traceback.format_exc())

# Create FastAPI app
app = FastAPI(
    title="A-MEM MCP Server",
    description="Memory Control Protocol server for Agentic Memory",
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

# Error handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Initialize memory system during startup
@app.on_event("startup")
async def startup_event():
    init_memory_system()

# Basic routes
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "memory_system": memory_system is not None}

# Memory API routes
@app.post("/api/v1/memories")
async def create_memory(request: Request):
    """Create a new memory"""
    if memory_system is None:
        raise HTTPException(status_code=500, detail="Memory system not initialized")
    
    try:
        # Parse JSON body
        body = await request.json()
        
        content = body.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Create memory
        memory_id = memory_system.create(
            content=content,
            tags=body.get("tags", []),
            category=body.get("category", "General")
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        logger.error(traceback.format_exc())
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

# MCP schema
@app.get("/mcp-schema")
async def mcp_schema():
    """Serve MCP schema for Claude integration"""
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_schema.json")
    try:
        with open(schema_path, "r") as f:
            schema = f.read()
        return JSONResponse(content=schema)
    except Exception as e:
        logger.error(f"Failed to load MCP schema: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load MCP schema: {str(e)}"}
        )

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    uvicorn.run("server_robust:app", host=settings.HOST, port=settings.PORT, log_level="debug")
