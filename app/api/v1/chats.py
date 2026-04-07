from fastapi import APIRouter
from app.schemas.schemas import ChatRequest
from app.services import llm_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/", tags=["Chat"])
async def chat(req: ChatRequest):
    logger.info(f"Chat request with provider: {req.provider}")
    try:
        response = await llm_service.generate(
            prompt=req.message,
            provider=req.provider
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise e