from app.models.schemas import ChatRequest
from app.services import llm_service


@app.post("/chat")
async def chat(req: ChatRequest):
    response = await llm_service.generate(
        prompt=req.message,
        provider=req.provider
    )
    return {"response": response}