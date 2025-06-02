from fastapi import FastAPI

app = FastAPI(title="Notification Service")
 
@app.get("/")
async def root():
    return {"message": "Notification Service is running"} 