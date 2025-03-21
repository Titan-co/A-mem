from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="A-MEM Simplified Server",
    description="A simplified server to test A-MEM",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "A-MEM Server is starting"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Only import routes after defining the basic endpoints
@app.on_event("startup")
async def startup_event():
    print("Server is starting up...")
    try:
        # Import only config here to avoid circular imports
        from config import settings
        print(f"Loaded settings: {settings.APP_NAME}")
    except Exception as e:
        print(f"Error loading config: {e}")

if __name__ == "__main__":
    print("Starting simplified A-MEM server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
