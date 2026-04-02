from fastapi import FastAPI
from app.routes import chat

app = FastAPI(title="LOOMRESUME API", description="An API for LLM-based resume analysis and generation", version="1.0.0")

app.include_router(chat.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "LOOMRESUME API is running 🚀"}