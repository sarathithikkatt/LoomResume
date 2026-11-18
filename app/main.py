from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import agents, chats, health, ingest, jd, refraction, resume
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
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database initialization deferred or failed: {e}")
    yield
    # Cleanup logic (if any) can go here
    logger.info(f"--- 🤖 Stopping {settings.PROJECT_NAME} ---")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API for LLM-based resume analysis and generation",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats.router, prefix=f"{settings.API_V1_STR}/chat")
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/health")
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents")
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest")
app.include_router(jd.router, prefix=f"{settings.API_V1_STR}/jd")
app.include_router(refraction.router, prefix=f"{settings.API_V1_STR}/refraction")
app.include_router(resume.router, prefix=f"{settings.API_V1_STR}/resume")

@app.get("/")
def root():
    return {"message": "LOOMRESUME API is running 🚀"}
