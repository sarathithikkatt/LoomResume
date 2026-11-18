"""Resume Generation and PDF Export API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.db.models import ResumeOutput
from app.schemas.schemas import (
    ResumeDetailResponse,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
    ResumeRenderPDFRequest,
)
from app.services.resume_service import resume_service

logger = get_logger(__name__)

router = APIRouter()


@router.post("/generate", tags=["Resume"], response_model=ResumeGenerateResponse)
async def generate_resume(
    req: ResumeGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate a tailored resume matching a Job Description session and selected lens."""
    logger.info(f"Resume generate request: user={req.user_id}, session={req.jd_session_id}")
    try:
        result = await resume_service.generate_resume_for_jd(
            jd_session_id=req.jd_session_id,
            user_id=req.user_id,
            db=db,
            lens=req.lens,
            top_experience_nodes=req.top_experience_nodes,
            top_projects=req.top_projects,
        )
        return ResumeGenerateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resume_id}", tags=["Resume"], response_model=ResumeDetailResponse)
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Retrieve the stored HTML content and metadata of a generated resume."""
    logger.info(f"Get resume request: id={resume_id}")
    record = db.query(ResumeOutput).filter(ResumeOutput.id == resume_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")

    return ResumeDetailResponse(
        resume_id=str(record.id),
        user_id=str(record.user_id),
        final_content=record.final_content,
        created_at=record.created_at.isoformat() if record.created_at else None,
    )


@router.get("/{resume_id}/pdf", tags=["Resume"])
def download_resume_pdf(resume_id: str, db: Session = Depends(get_db)):
    """Render and download the generated resume as a PDF file."""
    logger.info(f"Download resume PDF request: id={resume_id}")
    record = db.query(ResumeOutput).filter(ResumeOutput.id == resume_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")

    try:
        pdf_bytes = resume_service.render_pdf(record.final_content)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="resume_{resume_id}.pdf"'},
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF for resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"PDF rendering error: {e}")


@router.post("/render-pdf", tags=["Resume"])
def render_custom_pdf(req: ResumeRenderPDFRequest):
    """Directly render any HTML resume content into a PDF binary."""
    try:
        pdf_bytes = resume_service.render_pdf(req.html_content)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="resume.pdf"'},
        )
    except Exception as e:
        logger.error(f"Direct PDF render error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
