"""
Unit tests for DiffService — anti-hallucination guardrails.

These tests require no external services (no DB, no LLM, no API keys).
"""

import pytest
from app.services.diff_service import DiffService


@pytest.fixture
def svc():
    return DiffService()


# ── compute_diff ────────────────────────────────────────────────────


class TestComputeDiff:
    def test_identical_texts(self, svc):
        result = svc.compute_diff("hello world", "hello world")
        assert result["similarity_ratio"] == 1.0
        assert result["additions_count"] == 0
        assert result["deletions_count"] == 0

    def test_completely_different(self, svc):
        result = svc.compute_diff("alpha beta gamma", "one two three")
        assert result["similarity_ratio"] < 0.3
        assert result["deletions_count"] > 0
        assert result["additions_count"] > 0

    def test_partial_change(self, svc):
        original = "Built a data pipeline using Apache Spark"
        rewritten = "Designed a data pipeline leveraging Apache Spark"
        result = svc.compute_diff(original, rewritten)
        assert 0.4 < result["similarity_ratio"] < 1.0


# ── check_truncation ───────────────────────────────────────────────


class TestCheckTruncation:
    def test_not_truncated(self, svc):
        original = "Led team of 5 engineers to deliver the platform on time."
        rewritten = "Managed a team of 5 engineers, delivering the platform ahead of schedule."
        result = svc.check_truncation(original, rewritten)
        assert result["is_truncated"] is False
        assert result["ends_cleanly"] is True

    def test_severely_truncated(self, svc):
        original = "Built and deployed a microservices architecture serving 10M requests per day."
        rewritten = "Built a micro"
        result = svc.check_truncation(original, rewritten)
        assert result["is_truncated"] is True
        assert result["length_ratio"] < 0.6

    def test_ends_mid_sentence(self, svc):
        original = "Reduced latency by 40% through caching layer."
        rewritten = "Reduced latency by 40% through"  # no terminal punct, < 85% length
        result = svc.check_truncation(original, rewritten)
        assert result["ends_cleanly"] is False


# ── verify_facts ────────────────────────────────────────────────────


class TestVerifyFacts:
    def test_all_facts_preserved(self, svc):
        original = "Reduced latency by 40% using Redis and Python on AWS."
        rewritten = "Achieved a 40% latency reduction by implementing Redis caching in Python on AWS."
        result = svc.verify_facts(original, rewritten)
        assert result["passed"] is True
        assert len(result["missing_metrics"]) == 0
        assert len(result["missing_techs"]) == 0

    def test_missing_metric(self, svc):
        original = "Improved throughput by 300% and reduced errors by 50% using Kafka."
        rewritten = "Significantly improved throughput and reduced errors using Kafka."
        result = svc.verify_facts(original, rewritten)
        # 300% and 50% are missing
        assert len(result["missing_metrics"]) >= 1

    def test_missing_tech(self, svc):
        original = "Migrated infrastructure from AWS to GCP using Terraform and Docker."
        rewritten = "Migrated infrastructure to the cloud using infrastructure-as-code tools."
        result = svc.verify_facts(original, rewritten)
        assert result["passed"] is False
        assert len(result["missing_techs"]) > 0

    def test_no_facts_still_passes(self, svc):
        """Text with no extractable facts should still pass."""
        original = "Collaborated with cross-functional teams to deliver the project."
        rewritten = "Partnered with cross-functional teams to ship the project."
        result = svc.verify_facts(original, rewritten)
        assert result["passed"] is True


# ── full_verify ─────────────────────────────────────────────────────


class TestFullVerify:
    def test_good_refraction_passes(self, svc):
        original = "Built a CI/CD pipeline using Docker and Kubernetes, reducing deployment time by 60%."
        rewritten = "Architected a CI/CD pipeline leveraging Docker and Kubernetes, achieving a 60% reduction in deployment time."
        result = svc.full_verify(original, rewritten)
        assert result["passed"] is True
        assert result["facts"]["passed"] is True
        assert result["truncation"]["is_truncated"] is False

    def test_hallucinated_refraction_fails(self, svc):
        original = "Maintained a legacy Java application."
        rewritten = "Architected a microservices platform using Python and React, serving 50M users."
        result = svc.full_verify(original, rewritten)
        # The rewritten text fabricates techs and metrics not in original
        # This should fail on facts (Java is missing, Python/React are hallucinated additions)
        assert result["facts"]["passed"] is False or result["truncation"]["is_truncated"] is False
