from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import get_logger
from app.db.models import ExperienceNode, Project, SkillsProfile, User
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


@router.get("/vault", tags=["Ingest"])
def get_vault(db: Session = Depends(get_db)):
    """Retrieve all current vault data: user profile, experience nodes, projects, and skills."""
    user = db.query(User).first()
    if not user:
        return {"user": None, "nodes": [], "projects": [], "skills": []}

    nodes = db.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).all()
    projects = db.query(Project).filter(Project.user_id == user.id).all()
    skills = db.query(SkillsProfile).filter(SkillsProfile.user_id == user.id).all()

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "personal_info": user.personal_info,
            "summary": user.summary,
        },
        "nodes": [
            {
                "id": str(n.id),
                "company": n.company,
                "role": n.role,
                "duration": n.duration,
                "raw_text": n.raw_text,
                "tags": n.tags or [],
            }
            for n in nodes
        ],
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "tags": p.tags or [],
            }
            for p in projects
        ],
        "skills": [
            {
                "id": str(s.id),
                "skill_name": s.skill_name,
                "category": s.category,
            }
            for s in skills
        ],
    }
