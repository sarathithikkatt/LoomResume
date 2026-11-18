"""
Embedding service with support for multiple providers.

Supports:
- Ollama (local, free) — nomic-embed-text (768 dims)
- OpenAI — text-embedding-3-small (1536 dims)

Provider is auto-selected based on available config.
"""

import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Embedding dimensions per model
EMBEDDING_DIMS = {
    "nomic-embed-text": 768,
    "text-embedding-3-small": 1536,
}


class EmbeddingService:
    """Generates text embeddings via Ollama or OpenAI."""

    def __init__(self):
        self._provider: str | None = None
        self._model: str | None = None
        self._openai_client = None

        # Prefer Ollama (free, local) → then OpenAI
        if settings.EMBEDDING_PROVIDER == "ollama" or (
            settings.EMBEDDING_PROVIDER == "auto" and not settings.OPENAI_API_KEY
        ):
            self._provider = "ollama"
            self._model = settings.OLLAMA_EMBEDDING_MODEL
            logger.info(f"EmbeddingService initialised with Ollama ({self._model})")
        elif settings.OPENAI_API_KEY:
            self._provider = "openai"
            self._model = "text-embedding-3-small"
            try:
                from langchain_openai import OpenAIEmbeddings
                self._openai_client = OpenAIEmbeddings(
                    model=self._model,
                    api_key=settings.OPENAI_API_KEY,
                )
                logger.info("EmbeddingService initialised with OpenAI text-embedding-3-small")
            except ImportError:
                logger.error("langchain-openai not installed, falling back to Ollama")
                self._provider = "ollama"
                self._model = settings.OLLAMA_EMBEDDING_MODEL
        else:
            logger.warning(
                "No embedding provider configured. Set OLLAMA_EMBEDDING_MODEL or OPENAI_API_KEY. "
                "Vector search will not work."
            )

    @property
    def available(self) -> bool:
        return self._provider is not None

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensions for the current model."""
        return EMBEDDING_DIMS.get(self._model, 768)

    def embed_text(self, text: str) -> list[float] | None:
        """Embed a single text string."""
        if not self._provider:
            return None
        try:
            if self._provider == "ollama":
                return self._ollama_embed(text)
            else:
                return self._openai_client.embed_query(text)
        except Exception as e:
            logger.error(f"Embedding failed for text ({len(text)} chars): {e}")
            return None

    def embed_texts(self, texts: list[str]) -> list[list[float] | None]:
        """Embed a batch of texts."""
        if not self._provider:
            return [None] * len(texts)
        try:
            if self._provider == "ollama":
                return [self._ollama_embed(t) for t in texts]
            else:
                return self._openai_client.embed_documents(texts)
        except Exception as e:
            logger.error(f"Batch embedding failed ({len(texts)} texts): {e}")
            return [None] * len(texts)

    def _ollama_embed(self, text: str) -> list[float]:
        """Call Ollama embedding API synchronously."""
        response = httpx.post(
            f"{settings.OLLAMA_API_BASE}/api/embed",
            json={"model": self._model, "input": text},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"][0]


# Module-level singleton
embedding_service = EmbeddingService()
