from fastapi import APIRouter

from app.schemas.schemas import ChatRequest
from app.services import llm_service


router = APIRouter()

@router.post("/", tags=["Chat"])
async def chat(req: ChatRequest):
    response = await llm_service.generate(
        prompt=req.message,
        provider=req.provider
    )
    return {"response": response}