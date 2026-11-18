"""
Chat orchestration service for the LoomResume conversational interface.
"""

from app.core.logging import get_logger
from app.services.llm_service import llm_service

logger = get_logger(__name__)

LOOM_SYSTEM_PROMPT = """You are Loom, the AI Career Identity and Resume Architecture Assistant.
You treat the candidate's career history as a living database of achievements and metrics.

Your capabilities include:
1. Refracting experiences through distinct technical and business lenses (Platform, Infrastructure, Leadership, Business Impact, Data Engineering, Security).
2. Contextualizing candidate history against specific Job Descriptions (ATS keyword matching and semantic alignment).
3. Architecting evidence-based Gap-Filler Projects to bridge missing skill sets.
4. Structuring and generating tailored resumes and mock interview prep.

Tone: Professional, direct, high-signal, engineering-focused. Never invent accomplishments or numbers not provided by the candidate.
"""


class ChatService:
    """Manages chat requests with Loom identity context."""

    async def chat(
        self,
        message: str,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        effective_system_prompt = (
            f"{LOOM_SYSTEM_PROMPT}\n\n{system_prompt}" if system_prompt else LOOM_SYSTEM_PROMPT
        )
        logger.info(f"ChatService processing message: length={len(message)}")
        return await llm_service.generate(
            prompt=message,
            model=model,
            system_prompt=effective_system_prompt,
            temperature=temperature,
        )


# Module-level singleton
chat_service = ChatService()
