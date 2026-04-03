from fastapi import FastAPI

from app.api.v1 import chats, agents, health

app = FastAPI(title="LOOMRESUME API", description="An API for LLM-based resume analysis and generation", version="1.0.0")

app.include_router(chats.router, prefix="/api")
app.include_router(health.router, prefix="/health")
app.include_router(agents.router, prefix="/agents")

@app.get("/")
def root():
    return {"message": "LOOMRESUME API is running 🚀"}