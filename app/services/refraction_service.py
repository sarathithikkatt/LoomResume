"""
Role Refraction engine with anti-hallucination guardrails.

Reframes experience narratives through different "lenses" (platform, infrastructure,
leadership, business_impact) while ensuring factual accuracy via diff verification.
"""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import ExperienceNode, JDSession, Refraction
from app.services.diff_service import diff_service
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service

logger = get_logger(__name__)

# ── Lens Prompts ────────────────────────────────────────────────────

LENS_PROMPTS = {
    "platform": (
        "You are reframing a work experience bullet point through a PLATFORM ENGINEERING lens. "
        "Emphasize: scalability, system design, API architecture, infrastructure as code, "
        "developer experience, and platform reliability. "
    ),
    "infrastructure": (
        "You are reframing a work experience bullet point through an INFRASTRUCTURE lens. "
        "Emphasize: cloud architecture, deployment pipelines, monitoring, SRE practices, "
        "cost optimization, and operational excellence. "
    ),
    "leadership": (
        "You are reframing a work experience bullet point through a LEADERSHIP lens. "
        "Emphasize: team management, mentorship, cross-functional collaboration, "
        "decision-making, stakeholder communication, and strategic impact. "
    ),
    "business_impact": (
        "You are reframing a work experience bullet point through a BUSINESS IMPACT lens. "
        "Emphasize: revenue impact, cost savings, user growth, efficiency gains, "
        "market positioning, and measurable business outcomes. "
    ),
    "data_engineering": (
        "You are reframing a work experience bullet point through a DATA ENGINEERING lens. "
        "Emphasize: data pipelines, ETL/ELT, data modeling, analytics infrastructure, "
        "data quality, and data-driven decision making. "
    ),
    "security": (
        "You are reframing a work experience bullet point through a SECURITY lens. "
        "Emphasize: security architecture, compliance, threat modeling, access control, "
        "vulnerability management, and security best practices. "
    ),
}

REFRACTION_PROMPT = """{lens_prompt}

CRITICAL RULES:
1. PRESERVE all factual information: numbers, percentages, company names, technology names, dates
2. Do NOT invent new metrics, achievements, or technologies not present in the original
3. Do NOT drop any key achievements from the original
4. Reframe the NARRATIVE perspective, not the FACTS
5. Keep approximately the same length as the original

Original text:
---
{original_text}
---

Reframed text (respond with ONLY the reframed bullet point, no explanation):"""

MAX_RETRIES = 2


class RefractionService:
    """Reframes experience narratives through different lenses with anti-hallucination checks."""

    async def refract(
        self,
        experience_node_id: str,
        lens: str,
        user_id: str,
        db: Session,
        model: str | None = None,
    ) -> dict:
        """
        Refract a single experience node through a specified lens.

        Args:
            experience_node_id: UUID of the ExperienceNode
            lens: One of the supported lenses (platform, infrastructure, etc.)
            user_id: UUID of the user
            db: Database session
            model: Optional LLM model string

        Returns:
            Dict with refracted text, diff analysis, and verification results
        """
        # Validate lens
        lens = lens.lower().strip()
        if lens not in LENS_PROMPTS:
            raise ValueError(
                f"Unsupported lens: '{lens}'. Supported: {', '.join(LENS_PROMPTS.keys())}"
            )

        # Get the experience node
        node = db.query(ExperienceNode).filter(
            ExperienceNode.id == experience_node_id,
            ExperienceNode.user_id == user_id,
        ).first()
        if not node:
            raise ValueError(f"ExperienceNode not found: {experience_node_id}")

        original_text = node.raw_text

        # Attempt refraction with retries
        for attempt in range(MAX_RETRIES + 1):
            prompt = REFRACTION_PROMPT.format(
                lens_prompt=LENS_PROMPTS[lens],
                original_text=original_text,
            )

            # On retry, add stricter instructions
            if attempt > 0:
                prompt += (
                    f"\n\n⚠️ RETRY {attempt}/{MAX_RETRIES}: Your previous attempt "
                    f"failed verification. Be MORE careful to preserve ALL facts, "
                    f"numbers, and technology names from the original."
                )

            reframed_text = await llm_service.generate(
                prompt=prompt,
                model=model,
                temperature=0.5 - (attempt * 0.15),  # Lower temp on retries
            )

            # Run verification
            verification = diff_service.full_verify(original_text, reframed_text)

            if verification["passed"]:
                logger.info(
                    f"Refraction passed on attempt {attempt + 1}: "
                    f"similarity={verification['diff']['similarity_ratio']}"
                )
                break
            else:
                logger.warning(
                    f"Refraction attempt {attempt + 1} failed verification: "
                    f"facts_passed={verification['facts']['passed']}, "
                    f"truncated={verification['truncation']['is_truncated']}"
                )

        # Compute embedding for the refracted text
        emb = embedding_service.embed_text(reframed_text)

        # Upsert the refraction (unique on source_id + lens)
        existing = db.query(Refraction).filter(
            Refraction.source_id == experience_node_id,
            Refraction.lens == lens,
        ).first()

        if existing:
            existing.reframed_text = reframed_text
            existing.embedding = str(emb) if emb else None
            refraction = existing
        else:
            refraction = Refraction(
                source_id=experience_node_id,
                source_type="experience_node",
                user_id=user_id,
                lens=lens,
                reframed_text=reframed_text,
                embedding=str(emb) if emb else None,
            )
            db.add(refraction)

        db.flush()

        result = {
            "refraction_id": str(refraction.id),
            "source_id": str(experience_node_id),
            "lens": lens,
            "original_text": original_text,
            "reframed_text": reframed_text,
            "verification": verification,
            "attempts": attempt + 1,
        }

        db.commit()
        return result

    async def refract_for_jd(
        self,
        jd_session_id: str,
        user_id: str,
        db: Session,
        lens: str | None = None,
        top_k: int = 5,
        model: str | None = None,
    ) -> dict:
        """
        Find the top matching experience nodes for a JD and refract each one.

        If no lens is specified, auto-selects based on JD keywords.
        """
        from app.services.jd_service import jd_service  # deferred to avoid circular import

        # Get the JD session for keyword-based lens selection
        jd_session = db.query(JDSession).filter(JDSession.id == jd_session_id).first()
        if not jd_session:
            raise ValueError(f"JD session not found: {jd_session_id}")

        # Auto-select lens if not provided
        if not lens:
            lens = self._auto_select_lens(jd_session.keywords or [])

        # Find relevant nodes
        matches = jd_service.find_relevant_nodes(
            jd_session_id=jd_session_id,
            user_id=user_id,
            db=db,
            top_k=top_k,
        )

        if not matches:
            return {"lens": lens, "refractions": [], "message": "No matching experience nodes found"}

        # Refract each matching node
        refractions = []
        for match in matches:
            try:
                result = await self.refract(
                    experience_node_id=match["node_id"],
                    lens=lens,
                    user_id=user_id,
                    db=db,
                    model=model,
                )
                result["match_similarity"] = match["similarity"]
                refractions.append(result)
            except Exception as e:
                logger.error(f"Refraction failed for node {match['node_id']}: {e}")
                refractions.append({
                    "source_id": match["node_id"],
                    "error": str(e),
                    "match_similarity": match["similarity"],
                })

        return {
            "jd_session_id": jd_session_id,
            "lens": lens,
            "total_matches": len(matches),
            "successful_refractions": sum(1 for r in refractions if "error" not in r),
            "refractions": refractions,
        }

    def _auto_select_lens(self, keywords: list[str]) -> str:
        """Auto-select the best lens based on JD keywords."""
        keyword_set = {k.lower() for k in keywords}

        lens_signals = {
            "platform": {"api", "platform", "sdk", "developer", "scalability", "microservices", "service"},
            "infrastructure": {"aws", "gcp", "azure", "cloud", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "devops", "sre"},
            "leadership": {"lead", "manage", "mentor", "team", "director", "principal", "staff", "stakeholder"},
            "business_impact": {"revenue", "growth", "roi", "kpi", "conversion", "retention", "business"},
            "data_engineering": {"data", "pipeline", "etl", "analytics", "warehouse", "spark", "airflow", "bigquery"},
            "security": {"security", "compliance", "soc2", "gdpr", "encryption", "iam", "vulnerability"},
        }

        scores = {}
        for lens_name, signals in lens_signals.items():
            scores[lens_name] = len(keyword_set & signals)

        best_lens = max(scores, key=scores.get)
        if scores[best_lens] == 0:
            best_lens = "business_impact"  # safe default

        logger.info(f"Auto-selected lens: {best_lens} (scores: {scores})")
        return best_lens

    def get_diff(self, refraction_id: str, db: Session) -> dict:
        """Get the diff between original and refracted text for a given refraction."""
        refraction = db.query(Refraction).filter(Refraction.id == refraction_id).first()
        if not refraction:
            raise ValueError(f"Refraction not found: {refraction_id}")

        # Get the original text
        node = db.query(ExperienceNode).filter(
            ExperienceNode.id == refraction.source_id
        ).first()
        if not node:
            raise ValueError(f"Source node not found: {refraction.source_id}")

        return diff_service.full_verify(node.raw_text, refraction.reframed_text)


# Module-level singleton
refraction_service = RefractionService()
