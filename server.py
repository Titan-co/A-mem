from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import json
import os
from config import settings
from routes import router
import nltk

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Download necessary NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # Add routes
    app.include_router(router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint showing API information"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "docs": "/docs",
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.get("/mcp-schema")
    async def mcp_schema():
        """Serve MCP schema for Claude integration"""
        schema_path = os.path.join(os.path.dirname(__file__), "mcp_schema.json")
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
            return JSONResponse(content=schema)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to load MCP schema: {str(e)}"}
            )
    
    return app

app = create_app()

if __name__ == "__main__":
    """Run the server when the script is executed directly"""
    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
