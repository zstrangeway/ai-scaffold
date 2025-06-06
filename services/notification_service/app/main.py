from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Notification Service", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Notification Service is running", "service": "notification-service", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False) 