from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recommendation

app = FastAPI(title="what to cook API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://cook-assistant-beryl.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendation.router, prefix="/api", tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "what to cook API is running"}