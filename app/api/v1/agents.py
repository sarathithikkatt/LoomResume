from fastapi import APIRouter

router = APIRouter()

@router.post("/", tags=["Agents"])
async def agents():
    pass