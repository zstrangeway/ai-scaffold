from fastapi import FastAPI
import uvicorn

app = FastAPI(title="AI Service", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "AI Service is running", "service": "ai-service", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False) 