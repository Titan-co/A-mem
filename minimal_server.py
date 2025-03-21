"""Minimal FastAPI server to test if FastAPI and uvicorn work correctly"""
from fastapi import FastAPI
import uvicorn

# Create a minimal FastAPI app
app = FastAPI(
    title="A-MEM Minimal Test Server",
    description="A minimal server to test FastAPI and uvicorn",
    version="0.1.0"
)

# Define a simple root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "A-MEM Minimal Test Server is running",
        "endpoints": ["/", "/health"]
    }

# Define a health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run the server if this script is executed directly
if __name__ == "__main__":
    print("Starting minimal test server...")
    print("Try accessing:")
    print("  - http://localhost:8001/")
    print("  - http://localhost:8001/health")
    print("  - http://localhost:8001/docs")
    print("Press Ctrl+C to stop the server")
    
    # Run with error handling
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
