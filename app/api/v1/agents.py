from fastapi import APIRouter

router = APIRouter()

@router.post("/agents", tags=["Agents"])
async def agents():
    pass