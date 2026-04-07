from fastapi import APIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/", tags=["Agents"])
async def agents():
    logger.info("Agent endpoint called")
    pass