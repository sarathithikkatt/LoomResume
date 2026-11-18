from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/", tags=["Chat"], response_model=ChatResponse)
async def chat(req: ChatRequest):
    logger.info(f"Chat request → model={req.model}")
    try:
        response = await chat_service.chat(
            message=req.message,
            model=req.model,
            system_prompt=req.system_prompt,
            temperature=req.temperature,
        )
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
