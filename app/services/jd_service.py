"""
Job Description analysis and hybrid matching service.

Combines pgvector cosine similarity (semantic) with keyword set overlap (lexical/ATS)
to produce a comprehensive match score between a user's profile and a job description.
"""

import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import ExperienceNode, JDSession, Project, SkillsProfile, User
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service

logger = get_logger(__name__)

# ── Prompt Templates ────────────────────────────────────────────────

JD_ANALYSIS_PROMPT = """Analyze this job description and extract structured data.

Job Description:
---
{jd_text}
---

Return a JSON object with these fields:
{{
    "keywords": ["list", "of", "required", "technical", "skills"],
    "soft_skills": ["communication", "leadership", ...],
    "years_experience": "3-5 years" or null,
    "role_level": "Junior" | "Mid" | "Senior" | "Staff" | "Principal",
    "technologies": ["Python", "AWS", "Docker", ...],
    "domain": "fintech" | "healthtech" | "saas" | etc.
}}

Extract ALL technical keywords, frameworks, tools, and technologies mentioned.
Be exhaustive — include abbreviations and full names (e.g. both "k8s" and "Kubernetes").
"""


class JDService:
    """Job Description analysis and matching engine."""

    async def analyze_jd(self, jd_text: str, user_email: str, db: Session) -> dict:
        """
        Analyze a job description: extract keywords via LLM, compute embedding, store session.

        Returns the JDSession data as a dict.
        """
        # Find the user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise ValueError(f"User not found: {user_email}")

        # Extract structured data via LLM
        logger.info(f"Analyzing JD for user={user_email} ({len(jd_text)} chars)")
        analysis = await llm_service.generate_json(
            prompt=JD_ANALYSIS_PROMPT.format(jd_text=jd_text),
            system_prompt="You are an expert technical recruiter and ATS keyword optimizer.",
        )

        # Compute JD embedding
        jd_embedding = embedding_service.embed_text(jd_text)

        # Store the session
        session = JDSession(
            user_id=user.id,
            jd_text=jd_text,
            keywords=analysis.get("keywords", []) + analysis.get("technologies", []),
            jd_embedding=str(jd_embedding) if jd_embedding else None,
        )
        db.add(session)
        db.flush()

        result = {
            "session_id": str(session.id),
            "keywords": analysis.get("keywords", []),
            "soft_skills": analysis.get("soft_skills", []),
            "years_experience": analysis.get("years_experience"),
            "role_level": analysis.get("role_level", "Mid"),
            "technologies": analysis.get("technologies", []),
            "domain": analysis.get("domain"),
        }

        db.commit()
        logger.info(f"JD session created: {session.id} with {len(result['keywords'])} keywords")
        return result

    def score_match(self, jd_session_id: str, user_id: str, db: Session) -> dict:
        """
        Compute hybrid alignment score between a JD session and a user's profile.

        Returns:
            overall_score: weighted blend (0-100)
            semantic_score: pgvector cosine similarity average of top-K (0-100)
            keyword_score: keyword set overlap (0-100)
            present_keywords: keywords found in user's profile
            missing_keywords: keywords NOT found in user's profile
            top_matches: ranked experience nodes with similarity scores
        """
        session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not session:
            raise ValueError(f"JD session not found: {jd_session_id}")

        # ── Semantic Score (pgvector cosine similarity) ─────────────
        semantic_score = 0.0
        top_matches = []

        if session.jd_embedding:
            # Query experience nodes by cosine similarity
            embedding_str = session.jd_embedding if isinstance(session.jd_embedding, str) else str(session.jd_embedding)
            results = db.execute(
                text("""
                    SELECT id, company, role, raw_text,
                           1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                    FROM experience_nodes
                    WHERE user_id = :user_id AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 10
                """),
                {"embedding": embedding_str, "user_id": user_id},
            ).fetchall()

            if results:
                top_matches = [
                    {
                        "node_id": str(r.id),
                        "company": r.company,
                        "role": r.role,
                        "raw_text": r.raw_text[:200],
                        "similarity": round(float(r.similarity), 4),
                    }
                    for r in results
                ]
                # Average of top-5 similarities, scaled to 0-100
                top_sims = [float(r.similarity) for r in results[:5]]
                semantic_score = round((sum(top_sims) / len(top_sims)) * 100, 1)

            # Also check projects
            proj_results = db.execute(
                text("""
                    SELECT id, name, description,
                           1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                    FROM projects
                    WHERE user_id = :user_id AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 5
                """),
                {"embedding": embedding_str, "user_id": user_id},
            ).fetchall()

            if proj_results:
                for r in proj_results:
                    top_matches.append({
                        "node_id": str(r.id),
                        "company": "PROJECT",
                        "role": r.name,
                        "raw_text": (r.description or "")[:200],
                        "similarity": round(float(r.similarity), 4),
                    })

        # ── Keyword Score (set overlap) ─────────────────────────────
        jd_keywords = {k.lower().strip() for k in (session.keywords or [])}

        # Gather all user tags + skill names
        user_tags = set()
        exp_tags = db.query(ExperienceNode.tags).filter(
            ExperienceNode.user_id == user_id,
            ExperienceNode.tags.isnot(None),
        ).all()
        for (tags,) in exp_tags:
            if tags:
                user_tags.update(t.lower().strip() for t in tags)

        proj_tags = db.query(Project.tags).filter(
            Project.user_id == user_id,
            Project.tags.isnot(None),
        ).all()
        for (tags,) in proj_tags:
            if tags:
                user_tags.update(t.lower().strip() for t in tags)

        skill_names = db.query(SkillsProfile.skill_name).filter(
            SkillsProfile.user_id == user_id,
        ).all()
        for (name,) in skill_names:
            if name:
                user_tags.add(name.lower().strip())

        present = jd_keywords & user_tags
        missing = jd_keywords - user_tags
        keyword_score = round((len(present) / max(len(jd_keywords), 1)) * 100, 1)

        # ── Overall Score (weighted blend) ──────────────────────────
        overall_score = round(0.6 * semantic_score + 0.4 * keyword_score, 1)

        return {
            "overall_score": overall_score,
            "semantic_score": semantic_score,
            "keyword_score": keyword_score,
            "present_keywords": sorted(present),
            "missing_keywords": sorted(missing),
            "top_matches": sorted(top_matches, key=lambda x: x["similarity"], reverse=True),
        }

    def find_relevant_nodes(
        self, jd_session_id: str, user_id: str, db: Session, top_k: int = 10
    ) -> list[dict]:
        """Find the most relevant experience nodes for a JD using pgvector cosine similarity."""
        session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not session or not session.jd_embedding:
            return []

        embedding_str = session.jd_embedding if isinstance(session.jd_embedding, str) else str(session.jd_embedding)
        results = db.execute(
            text("""
                SELECT id, company, role, raw_text, tags,
                       1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                FROM experience_nodes
                WHERE user_id = :user_id AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {"embedding": embedding_str, "user_id": user_id, "top_k": top_k},
        ).fetchall()

        return [
            {
                "node_id": str(r.id),
                "company": r.company,
                "role": r.role,
                "raw_text": r.raw_text,
                "tags": r.tags,
                "similarity": round(float(r.similarity), 4),
            }
            for r in results
        ]


# Module-level singleton
jd_service = JDService()
