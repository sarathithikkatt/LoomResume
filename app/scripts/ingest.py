"""
Ingestion script for LoomResume.

Parses data/master_profile.json and seeds the database with:
- User record
- ExperienceNode records (one per bullet point)
- Project records
- SkillsProfile records

Usage:
    python -m app.scripts.ingest
"""

import json
import os
import sys

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import get_logger, setup_logging
from app.db.models import ExperienceNode, Project, SkillsProfile, User
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DEFAULT_PROFILE_PATH = os.path.join(DATA_DIR, "master_profile.json")


def load_profile(path: str) -> dict:
    """Load the master profile JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_create_user(db: Session, profile: dict) -> User:
    """Find existing user by email or create a new one."""
    email = profile["personal_info"]["email"]
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.info(f"Found existing user: {email} (id={user.id})")
        user.personal_info = profile["personal_info"]
        user.summary = profile.get("summary")
    else:
        user = User(
            email=email,
            personal_info=profile["personal_info"],
            summary=profile.get("summary"),
        )
        db.add(user)
        logger.info(f"Created new user: {email}")
    db.flush()  # ensure user.id is available
    return user


def clear_user_data(db: Session, user_id) -> dict:
    """Delete existing records for a user to allow clean re-ingestion."""
    counts = {}
    counts["experience_nodes"] = db.query(ExperienceNode).filter(ExperienceNode.user_id == user_id).delete()
    counts["projects"] = db.query(Project).filter(Project.user_id == user_id).delete()
    counts["skills"] = db.query(SkillsProfile).filter(SkillsProfile.user_id == user_id).delete()
    logger.info(f"Cleared existing data for user {user_id}: {counts}")
    return counts


def ingest_experience(db: Session, user_id, experience_entries: list) -> int:
    """Create ExperienceNode records — one per bullet point."""
    texts_to_embed = []
    nodes = []

    for entry in experience_entries:
        company = entry["company"]
        role = entry["role"]
        duration = entry.get("duration")

        for bullet in entry.get("bullets", []):
            raw_text = bullet["text"]
            tags = bullet.get("tags", [])
            texts_to_embed.append(raw_text)
            nodes.append({
                "company": company,
                "role": role,
                "duration": duration,
                "raw_text": raw_text,
                "tags": tags,
            })

    # Batch embed all bullet texts
    embeddings = embedding_service.embed_texts(texts_to_embed)

    for node_data, emb in zip(nodes, embeddings):
        node = ExperienceNode(
            user_id=user_id,
            company=node_data["company"],
            role=node_data["role"],
            duration=node_data["duration"],
            raw_text=node_data["raw_text"],
            tags=node_data["tags"],
            embedding=str(emb) if emb else None,
        )
        db.add(node)

    return len(nodes)


def ingest_projects(db: Session, user_id, projects: list) -> int:
    """Create Project records."""
    texts = [p["description"] for p in projects]
    embeddings = embedding_service.embed_texts(texts)

    for proj, emb in zip(projects, embeddings):
        record = Project(
            user_id=user_id,
            name=proj["name"],
            description=proj["description"],
            tags=proj.get("tags", []),
            embedding=str(emb) if emb else None,
        )
        db.add(record)

    return len(projects)


def ingest_skills(db: Session, user_id, skills: dict) -> int:
    """Create SkillsProfile records — one per skill."""
    count = 0
    for category, skill_list in skills.items():
        for skill_name in skill_list:
            record = SkillsProfile(
                user_id=user_id,
                skill_name=skill_name,
                category=category,
            )
            db.add(record)
            count += 1
    return count


def run_ingestion(profile_path: str = DEFAULT_PROFILE_PATH) -> dict:
    """Execute the full ingestion pipeline. Returns a summary dict."""
    logger.info(f"Starting ingestion from: {profile_path}")
    profile = load_profile(profile_path)

    db = SessionLocal()
    try:
        user = get_or_create_user(db, profile)
        cleared = clear_user_data(db, user.id)

        exp_count = ingest_experience(db, user.id, profile.get("experience", []))
        proj_count = ingest_projects(db, user.id, profile.get("projects", []))
        skill_count = ingest_skills(db, user.id, profile.get("skills", {}))

        db.commit()

        summary = {
            "user_email": user.email,
            "user_id": str(user.id),
            "cleared": cleared,
            "created": {
                "experience_nodes": exp_count,
                "projects": proj_count,
                "skills": skill_count,
            },
            "embeddings_enabled": embedding_service.available,
        }

        logger.info(f"Ingestion complete: {summary}")
        return summary

    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROFILE_PATH
    result = run_ingestion(path)
    print("\n" + "=" * 60)
    print("  INGESTION SUMMARY")
    print("=" * 60)
    print(f"  User:       {result['user_email']} ({result['user_id']})")
    print(f"  Cleared:    {result['cleared']}")
    print(f"  Created:    {result['created']}")
    print(f"  Embeddings: {'✅ Enabled' if result['embeddings_enabled'] else '⚠️  Disabled (no OPENAI_API_KEY)'}")
    print("=" * 60)
