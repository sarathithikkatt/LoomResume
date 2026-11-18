"""
Unit tests for RetrievalService.
"""

from unittest.mock import MagicMock
import pytest
from app.services.retrieval_service import RetrievalService


@pytest.fixture
def retrieval_svc():
    return RetrievalService()


class TestRetrievalService:
    def test_search_experience_nodes_by_embedding(self, retrieval_svc):
        mock_db = MagicMock()
        mock_row = MagicMock()
        mock_row.id = "11111111-1111-1111-1111-111111111111"
        mock_row.company = "One Impression"
        mock_row.role = "Platform Engineer"
        mock_row.duration = "2025 - 2026"
        mock_row.raw_text = "Migrated from EC2 to ECS."
        mock_row.tags = ["AWS", "ECS"]
        mock_row.similarity = 0.885

        mock_db.execute.return_value.fetchall.return_value = [mock_row]

        results = retrieval_svc.search_experience_nodes_by_embedding(
            db=mock_db,
            user_id="user-123",
            embedding=[0.1] * 768,
            limit=5,
        )

        assert len(results) == 1
        assert results[0]["company"] == "One Impression"
        assert results[0]["similarity"] == 0.885
        assert results[0]["node_id"] == "11111111-1111-1111-1111-111111111111"

    def test_search_projects_by_embedding(self, retrieval_svc):
        mock_db = MagicMock()
        mock_row = MagicMock()
        mock_row.id = "22222222-2222-2222-2222-222222222222"
        mock_row.name = "Video Transcoder"
        mock_row.description = "Go-based video transcoding"
        mock_row.tags = ["Go"]
        mock_row.similarity = 0.92

        mock_db.execute.return_value.fetchall.return_value = [mock_row]

        results = retrieval_svc.search_projects_by_embedding(
            db=mock_db,
            user_id="user-123",
            embedding=[0.1] * 768,
            limit=3,
        )

        assert len(results) == 1
        assert results[0]["name"] == "Video Transcoder"
        assert results[0]["similarity"] == 0.92

    def test_get_refractions_for_nodes_empty(self, retrieval_svc):
        mock_db = MagicMock()
        result = retrieval_svc.get_refractions_for_nodes(
            db=mock_db,
            user_id="user-123",
            node_ids=[],
            lens="platform",
        )
        assert result == {}
