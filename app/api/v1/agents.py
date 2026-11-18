"""Career advising and gap-filler project architecting API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.schemas import (
    GapProjectRequest,
    GapProjectResponse,
    MockInterviewRequest,
    MockInterviewResponse,
)
from app.services.agent_service import agent_service

logger = get_logger(__name__)

router = APIRouter()


@router.post("/gap-project", tags=["Agents"], response_model=GapProjectResponse)
async def create_gap_filler_project(
    req: GapProjectRequest,
    db: Session = Depends(get_db),
):
    """Architect a production-grade gap-filler project to bridge missing skills for a target JD."""
    logger.info(f"Gap-filler request: user={req.user_id}, session={req.jd_session_id}")
    try:
        result = await agent_service.architect_gap_filler_project(
            jd_session_id=req.jd_session_id,
            user_id=req.user_id,
            db=db,
            model=req.model,
        )
        return GapProjectResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Gap project architecting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mock-interview", tags=["Agents"], response_model=MockInterviewResponse)
async def generate_mock_interview(
    req: MockInterviewRequest,
    db: Session = Depends(get_db),
):
    """Generate scenario-based mock interview questions tailored to a target JD."""
    logger.info(f"Mock interview request: user={req.user_id}, session={req.jd_session_id}")
    try:
        result = await agent_service.generate_mock_interview(
            jd_session_id=req.jd_session_id,
            user_id=req.user_id,
            db=db,
            model=req.model,
        )
        return MockInterviewResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Mock interview generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
