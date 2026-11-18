"""JD analysis and matching API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.schemas import (
    JDAnalyzeRequest,
    JDAnalyzeResponse,
    JDMatchResponse,
    JDScoreResponse,
)
from app.services.jd_service import jd_service

logger = get_logger(__name__)

router = APIRouter()


@router.post("/analyze", tags=["JD"], response_model=JDAnalyzeResponse)
async def analyze_jd(req: JDAnalyzeRequest, db: Session = Depends(get_db)):
    """Submit a job description for analysis — extracts keywords, computes embedding, creates session."""
    logger.info(f"JD analyze request for user={req.user_email}")
    try:
        result = await jd_service.analyze_jd(
            jd_text=req.jd_text,
            user_email=req.user_email,
            db=db,
        )
        return JDAnalyzeResponse(
            session_id=result["session_id"],
            keywords=result["keywords"],
            role_level=result["role_level"],
            technologies=result["technologies"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"JD analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/score", tags=["JD"], response_model=JDScoreResponse)
def score_jd(session_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get the hybrid match score and keyword gap analysis for a JD session."""
    logger.info(f"JD score request: session={session_id}, user={user_id}")
    try:
        result = jd_service.score_match(
            jd_session_id=session_id,
            user_id=user_id,
            db=db,
        )
        return JDScoreResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"JD scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/matches", tags=["JD"], response_model=JDMatchResponse)
def match_jd(session_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get ranked relevant experience nodes for a JD session."""
    logger.info(f"JD match request: session={session_id}, user={user_id}")
    try:
        matches = jd_service.find_relevant_nodes(
            jd_session_id=session_id,
            user_id=user_id,
            db=db,
        )
        return JDMatchResponse(matches=matches)
    except Exception as e:
        logger.error(f"JD matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
