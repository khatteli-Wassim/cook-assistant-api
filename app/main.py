from fastapi import FastAPI
from app.routers import recommendation

app = FastAPI(title="what to cook API", version="1.0.0")

app.include_router(recommendation.router, prefix="/api", tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "what to cook API is running"}
