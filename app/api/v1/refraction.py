"""Refraction API endpoints — reframe experience narratives through different lenses."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.services.refraction_service import refraction_service

logger = get_logger(__name__)

router = APIRouter()


# ── Request/Response Models ─────────────────────────────────────────

class RefractRequest(BaseModel):
    experience_node_id: str
    lens: str  # platform, infrastructure, leadership, business_impact, data_engineering, security
    user_id: str
    model: str | None = None


class RefractForJDRequest(BaseModel):
    user_id: str
    lens: str | None = None  # auto-selected if not provided
    top_k: int = 5
    model: str | None = None


class RefractResponse(BaseModel):
    refraction_id: str
    source_id: str
    lens: str
    original_text: str
    reframed_text: str
    verification: dict
    attempts: int


class JDRefractResponse(BaseModel):
    jd_session_id: str
    lens: str
    total_matches: int
    successful_refractions: int
    refractions: list[dict]


class DiffResponse(BaseModel):
    passed: bool
    diff: dict
    truncation: dict
    facts: dict


# ── Endpoints ───────────────────────────────────────────────────────

@router.post("/", tags=["Refraction"], response_model=RefractResponse)
async def refract(req: RefractRequest, db: Session = Depends(get_db)):
    """Refract a single experience node through a specified lens."""
    logger.info(f"Refraction request: node={req.experience_node_id}, lens={req.lens}")
    try:
        result = await refraction_service.refract(
            experience_node_id=req.experience_node_id,
            lens=req.lens,
            user_id=req.user_id,
            db=db,
            model=req.model,
        )
        return RefractResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Refraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jd/{session_id}", tags=["Refraction"], response_model=JDRefractResponse)
async def refract_for_jd(
    session_id: str,
    req: RefractForJDRequest,
    db: Session = Depends(get_db),
):
    """Refract all matching experience nodes for a JD session."""
    logger.info(f"JD refraction request: session={session_id}, user={req.user_id}")
    try:
        result = await refraction_service.refract_for_jd(
            jd_session_id=session_id,
            user_id=req.user_id,
            db=db,
            lens=req.lens,
            top_k=req.top_k,
            model=req.model,
        )
        return JDRefractResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"JD refraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{refraction_id}/diff", tags=["Refraction"], response_model=DiffResponse)
def get_diff(refraction_id: str, db: Session = Depends(get_db)):
    """Get the verification diff between original and refracted text."""
    logger.info(f"Diff request: refraction={refraction_id}")
    try:
        result = refraction_service.get_diff(
            refraction_id=refraction_id,
            db=db,
        )
        return DiffResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Diff retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
