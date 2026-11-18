"""
Retrieval service for semantic, keyword, and hybrid search across ExperienceNodes, Projects, and Refractions.
"""

from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.db.models import Refraction

logger = get_logger(__name__)


class RetrievalService:
    """Encapsulates pgvector vector search and relational queries for career data."""

    def search_experience_nodes_by_embedding(
        self,
        db: Session,
        user_id: str,
        embedding: list[float] | str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Query experience nodes by pgvector cosine similarity."""
        embedding_str = embedding if isinstance(embedding, str) else str(embedding)
        query = text("""
            SELECT id, company, role, duration, raw_text, tags,
                   1 - (embedding <=> :embedding::vector) as similarity
            FROM experience_nodes
            WHERE user_id = :user_id AND embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        results = db.execute(
            query,
            {"embedding": embedding_str, "user_id": user_id, "limit": limit},
        ).fetchall()

        return [
            {
                "id": str(r.id),
                "node_id": str(r.id),
                "company": r.company,
                "role": r.role,
                "duration": r.duration,
                "raw_text": r.raw_text,
                "tags": r.tags or [],
                "similarity": round(float(r.similarity), 4),
            }
            for r in results
        ]

    def search_projects_by_embedding(
        self,
        db: Session,
        user_id: str,
        embedding: list[float] | str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Query projects by pgvector cosine similarity."""
        embedding_str = embedding if isinstance(embedding, str) else str(embedding)
        query = text("""
            SELECT id, name, description, tags,
                   1 - (embedding <=> :embedding::vector) as similarity
            FROM projects
            WHERE user_id = :user_id AND embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        results = db.execute(
            query,
            {"embedding": embedding_str, "user_id": user_id, "limit": limit},
        ).fetchall()

        return [
            {
                "id": str(r.id),
                "project_id": str(r.id),
                "name": r.name,
                "description": r.description,
                "tags": r.tags or [],
                "similarity": round(float(r.similarity), 4),
            }
            for r in results
        ]

    def get_refractions_for_nodes(
        self,
        db: Session,
        user_id: str,
        node_ids: list[str],
        lens: str,
    ) -> dict[str, str]:
        """Fetch refractions for a given set of experience node IDs and lens."""
        if not node_ids:
            return {}
        refractions = db.query(Refraction).filter(
            Refraction.user_id == user_id,
            Refraction.lens == lens,
            Refraction.source_id.in_(node_ids),
        ).all()
        return {str(r.source_id): r.reframed_text for r in refractions}


# Module-level singleton
retrieval_service = RetrievalService()
