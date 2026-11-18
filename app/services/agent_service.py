"""
Agent service for Career Advising, Gap-Filler Project Architecting, and Mock Interviews.
"""

from typing import Any
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import JDSession, User
from app.services.jd_service import jd_service
from app.services.llm_service import llm_service

logger = get_logger(__name__)

GAP_PROJECT_PROMPT = """You are a Principal Staff Engineer and Technical Career Architect.
Design a high-signal, production-grade gap-filler project to bridge the candidate's skill gaps for a target role.

Target Role / Level: {role_level}
Target Domain: {domain}
Missing Skills / Keyword Gaps: {missing_skills}
Existing Candidate Skills: {existing_skills}

Generate a comprehensive project blueprint as a JSON object with the following schema:
{{
    "project_name": "Concise, impactful system name",
    "tagline": "One-sentence pitch demonstrating real-world value",
    "architecture_summary": "System design overview (components, protocols, event flow)",
    "technologies": ["List", "of", "technologies", "used"],
    "milestones": [
        {{
            "phase": "Phase 1: Setup & Data Ingestion",
            "deliverables": ["deliverable 1", "deliverable 2"]
        }},
        {{
            "phase": "Phase 2: Core Processing & Scale",
            "deliverables": ["deliverable 1", "deliverable 2"]
        }}
    ],
    "metrics_to_measure": ["Latency reduction", "Throughput target", "Fault tolerance scenario"],
    "resume_bullet_points": [
        "Architected and deployed [System] using [Tech] to achieve [Metric]",
        "Engineered concurrent pipeline handling [X] with [Tech]"
    ]
}}
"""

MOCK_INTERVIEW_PROMPT = """You are a Technical Hiring Bar-Raiser interviewing a candidate for a {role_level} position.
Target Skills: {skills}

Generate 4 deep, scenario-based technical interview questions that test the candidate's real-world architectural thinking and trade-off decisions.

Return a JSON object:
{{
    "questions": [
        {{
            "topic": "System Design / Scalability / Incident Handling",
            "question": "The scenario question",
            "what_to_look_for": "Key signals of strong vs weak answers"
        }}
    ]
}}
"""


class AgentService:
    """Provides career guidance, project architecting, and interview preparation."""

    async def architect_gap_filler_project(
        self,
        jd_session_id: str,
        user_id: str,
        db: Session,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze JD session gaps and architect a tailored, evidence-based project.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not session:
            raise ValueError(f"JD Session not found: {jd_session_id}")

        # Compute match score to extract missing keywords
        score_data = jd_service.score_match(jd_session_id=jd_session_id, user_id=user_id, db=db)
        missing = score_data.get("missing_keywords", [])
        present = score_data.get("present_keywords", [])

        if not missing:
            missing_skills_str = "Advanced scalability, event-driven architecture, and zero-downtime reliability"
        else:
            missing_skills_str = ", ".join(missing[:8])

        existing_skills_str = ", ".join(present[:10]) if present else "General Backend Engineering"

        prompt = GAP_PROJECT_PROMPT.format(
            role_level="Senior / Lead Engineer",
            domain="Distributed Systems / Platform",
            missing_skills=missing_skills_str,
            existing_skills=existing_skills_str,
        )

        logger.info(f"Architecting gap project for user={user_id}, missing={missing_skills_str}")
        project_blueprint = await llm_service.generate_json(
            prompt=prompt,
            model=model,
            system_prompt="You are an elite Staff Software Architect designing high-signal technical projects.",
        )

        return {
            "jd_session_id": jd_session_id,
            "user_id": user_id,
            "targeted_gaps": missing[:8],
            "project_blueprint": project_blueprint,
        }

    async def generate_mock_interview(
        self,
        jd_session_id: str,
        user_id: str,
        db: Session,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Generate targeted technical interview questions based on the target JD."""
        session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not session:
            raise ValueError(f"JD Session not found: {jd_session_id}")

        keywords_str = ", ".join((session.keywords or [])[:8]) or "Distributed Systems, Microservices"

        prompt = MOCK_INTERVIEW_PROMPT.format(
            role_level="Senior Engineer",
            skills=keywords_str,
        )

        interview_data = await llm_service.generate_json(
            prompt=prompt,
            model=model,
            system_prompt="You are a seasoned Principal Engineer conducting high-signal technical interviews.",
        )

        return {
            "jd_session_id": jd_session_id,
            "target_skills": (session.keywords or [])[:8],
            "interview_questions": interview_data.get("questions", []),
        }


# Module-level singleton
agent_service = AgentService()
