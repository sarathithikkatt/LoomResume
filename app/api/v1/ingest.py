from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.logging import get_logger
from app.scripts.ingest import run_ingestion, DEFAULT_PROFILE_PATH

logger = get_logger(__name__)

router = APIRouter()


class IngestRequest(BaseModel):
    profile_path: str | None = None


class IngestResponse(BaseModel):
    status: str
    summary: dict


@router.post("/", tags=["Ingest"], response_model=IngestResponse)
async def ingest(req: IngestRequest | None = None):
    """Trigger the master profile ingestion pipeline."""
    path = (req.profile_path if req and req.profile_path else DEFAULT_PROFILE_PATH)
    logger.info(f"Ingest endpoint triggered with path={path}")
    try:
        summary = run_ingestion(path)
        return IngestResponse(status="success", summary=summary)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Profile not found: {path}")
    except Exception as e:
        logger.error(f"Ingest endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
