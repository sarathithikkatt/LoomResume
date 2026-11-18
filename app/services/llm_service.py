"""
Unified LLM service via LiteLLM.

Supports 100+ providers through a single interface.
Model string convention: "gpt-4o", "claude-sonnet-4-20250514", "ollama/llama3.1", "deepseek/deepseek-chat"
"""

import json

import litellm
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── LiteLLM configuration ──────────────────────────────────────────
litellm.drop_params = True  # silently drop unsupported params per provider

# Set API keys from settings so LiteLLM picks them up automatically
if settings.OPENAI_API_KEY:
    litellm.openai_key = settings.OPENAI_API_KEY
if settings.ANTHROPIC_API_KEY:
    litellm.anthropic_key = settings.ANTHROPIC_API_KEY


class LLMService:
    """Unified LLM service — one method, any provider."""

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Send a prompt to any LiteLLM-supported model and return the response text."""
        model = model or settings.LLM_DEFAULT_MODEL
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"LLM call → model={model}, temp={temperature}")

        # For Ollama models, set the api_base
        kwargs = {}
        if model.startswith("ollama"):
            kwargs["api_base"] = settings.OLLAMA_API_BASE

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        content = response.choices[0].message.content
        logger.info(f"LLM response ← {len(content)} chars")
        return content

    async def generate_json(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> dict:
        """Generate a response and parse it as JSON. Used for structured extraction."""
        raw = await self.generate(
            prompt=prompt,
            model=model,
            system_prompt=(system_prompt or "") + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
            temperature=temperature,
        )
        # Robustly extract JSON from response
        cleaned = raw.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start : end + 1].strip()
        return json.loads(cleaned)


# Module-level singleton
llm_service = LLMService()
