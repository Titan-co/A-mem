from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import traceback
from config import settings

def create_test_app():
    """Create a test application with minimal functionality"""
    app = FastAPI(
        title="A-MEM Test Server",
        description="A test server for A-MEM with minimal functionality",
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
    
    @app.get("/")
    async def root():
        return {
            "name": "A-MEM Test Server",
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/api/v1/test")
    async def test_endpoint():
        return {"message": "Test endpoint working!"}
    
    return app

app = create_test_app()

# Try to import routes using a safer approach
@app.on_event("startup")
async def startup_event():
    try:
        # We'll try to import memory_system and initialize it
        from memory_system import AgenticMemorySystem
        
        print("Initializing memory system...")
        memory_system = AgenticMemorySystem(
            model_name=settings.MODEL_NAME,
            llm_backend=settings.LLM_BACKEND,
            llm_model=settings.LLM_MODEL,
            evo_threshold=settings.EVO_THRESHOLD,
            api_key=settings.API_KEY
        )
        print("Memory system initialized successfully!")
        
        # Now try to set up a simple endpoint that uses the memory system
        @app.get("/api/v1/memory/test")
        async def test_memory():
            try:
                content = "Test memory created by test server"
                memory_id = memory_system.create(content=content, tags=["test"])
                return {
                    "status": "success", 
                    "message": "Memory created successfully",
                    "memory_id": memory_id
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error creating memory: {str(e)}"
                }
                
    except Exception as e:
        print(f"Error in startup event: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    print("Starting A-MEM test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
