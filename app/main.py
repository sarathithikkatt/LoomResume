from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import chats, agents, health
from app.core.database import init_db
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database on startup
    logger.info(f"--- 🤖 Starting {settings.PROJECT_NAME} ---")
    init_db()
    yield
    # Cleanup logic (if any) can go here
    logger.info(f"--- 🤖 Stopping {settings.PROJECT_NAME} ---")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API for LLM-based resume analysis and generation",
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(chats.router, prefix="/chat")
app.include_router(health.router, prefix="/health")
app.include_router(agents.router, prefix="/agents")

@app.get("/")
def root():
    return {"message": "LOOMRESUME API is running 🚀"}