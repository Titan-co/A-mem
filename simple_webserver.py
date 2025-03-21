from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "A-MEM Server test is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting simple test server...")
    print("Test the server by navigating to http://localhost:8080/ in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8080)
