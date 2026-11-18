from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logging import get_logger
from app.db.models import ExperienceNode, Project, SkillsProfile, User
from app.scripts.ingest import run_ingestion, DEFAULT_PROFILE_PATH
from app.schemas.schemas import (
    ExperienceNodeCreate,
    ExperienceNodeUpdate,
    ProjectCreate,
    ProjectUpdate,
    SkillCreate,
    UserProfileUpdate,
)
from app.services.embedding_service import embedding_service

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


# ── Experience Node CRUD Endpoints ──────────────────────────────────

@router.post("/nodes", tags=["Vault Editor"])
def create_experience_node(req: ExperienceNodeCreate, db: Session = Depends(get_db)):
    """Create a new experience achievement bullet and automatically generate its dense vector embedding."""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")

    emb = embedding_service.embed_text(req.raw_text)
    node = ExperienceNode(
        user_id=user.id,
        company=req.company,
        role=req.role,
        duration=req.duration,
        raw_text=req.raw_text,
        tags=req.tags,
        embedding=str(emb) if emb else None,
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    return {
        "id": str(node.id),
        "company": node.company,
        "role": node.role,
        "duration": node.duration,
        "raw_text": node.raw_text,
        "tags": node.tags or [],
    }


@router.put("/nodes/{node_id}", tags=["Vault Editor"])
def update_experience_node(node_id: str, req: ExperienceNodeUpdate, db: Session = Depends(get_db)):
    """Update an existing experience node, refreshing its dense vector embedding if text changed."""
    node = db.query(ExperienceNode).filter(ExperienceNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail=f"Experience node not found: {node_id}")

    if req.company is not None:
        node.company = req.company
    if req.role is not None:
        node.role = req.role
    if req.duration is not None:
        node.duration = req.duration
    if req.tags is not None:
        node.tags = req.tags
    if req.raw_text is not None and req.raw_text != node.raw_text:
        node.raw_text = req.raw_text
        emb = embedding_service.embed_text(req.raw_text)
        if emb:
            node.embedding = str(emb)

    db.commit()
    db.refresh(node)

    return {
        "id": str(node.id),
        "company": node.company,
        "role": node.role,
        "duration": node.duration,
        "raw_text": node.raw_text,
        "tags": node.tags or [],
    }


@router.delete("/nodes/{node_id}", tags=["Vault Editor"])
def delete_experience_node(node_id: str, db: Session = Depends(get_db)):
    """Delete an experience node from the vault."""
    node = db.query(ExperienceNode).filter(ExperienceNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail=f"Experience node not found: {node_id}")

    db.delete(node)
    db.commit()
    return {"status": "deleted", "id": node_id}


# ── Skills Profile CRUD Endpoints ───────────────────────────────────

@router.post("/skills", tags=["Vault Editor"])
def create_skill(req: SkillCreate, db: Session = Depends(get_db)):
    """Add a new technical or functional skill to the candidate profile."""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")

    skill = SkillsProfile(
        user_id=user.id,
        skill_name=req.skill_name.strip(),
        category=req.category or "Technical Skills",
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return {
        "id": str(skill.id),
        "skill_name": skill.skill_name,
        "category": skill.category,
    }


@router.delete("/skills/{skill_id}", tags=["Vault Editor"])
def delete_skill(skill_id: str, db: Session = Depends(get_db)):
    """Remove a skill from the candidate profile."""
    skill = db.query(SkillsProfile).filter(SkillsProfile.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")

    db.delete(skill)
    db.commit()
    return {"status": "deleted", "id": skill_id}


# ── Projects CRUD Endpoints ─────────────────────────────────────────

@router.post("/projects", tags=["Vault Editor"])
def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project in the vault with dense vector embedding."""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")

    emb = embedding_service.embed_text(req.description)
    project = Project(
        user_id=user.id,
        name=req.name,
        description=req.description,
        tags=req.tags,
        embedding=str(emb) if emb else None,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "tags": project.tags or [],
    }


@router.put("/projects/{project_id}", tags=["Vault Editor"])
def update_project(project_id: str, req: ProjectUpdate, db: Session = Depends(get_db)):
    """Update an existing project and refresh its vector embedding if description changed."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    if req.name is not None:
        project.name = req.name
    if req.tags is not None:
        project.tags = req.tags
    if req.description is not None and req.description != project.description:
        project.description = req.description
        emb = embedding_service.embed_text(req.description)
        if emb:
            project.embedding = str(emb)

    db.commit()
    db.refresh(project)

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "tags": project.tags or [],
    }


@router.delete("/projects/{project_id}", tags=["Vault Editor"])
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a project from the vault."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    db.delete(project)
    db.commit()
    return {"status": "deleted", "id": project_id}


# ── User Profile / Summary Update ───────────────────────────────────

@router.put("/profile", tags=["Vault Editor"])
def update_profile(req: UserProfileUpdate, db: Session = Depends(get_db)):
    """Update candidate personal info and master career summary."""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")

    if req.summary is not None:
        user.summary = req.summary

    info = dict(user.personal_info or {})
    if req.name is not None:
        info["name"] = req.name
    if req.label is not None:
        info["label"] = req.label
    if req.phone is not None:
        info["phone"] = req.phone
    if req.location is not None:
        info["location"] = req.location
    if req.linkedin is not None:
        info["linkedin"] = req.linkedin
    if req.github is not None:
        info["github"] = req.github

    user.personal_info = info
    db.commit()
    db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "personal_info": user.personal_info,
        "summary": user.summary,
    }
