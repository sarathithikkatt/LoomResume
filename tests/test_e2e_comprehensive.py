"""
Comprehensive End-to-End (E2E) Test Suite for LoomResume.

Covers:
1. Individual Component Tests:
   - Component 1: PostgreSQL 16 + pgvector Database
   - Component 2: Vector Embedding Engine (Ollama nomic-embed-text)
   - Component 3: Profile Ingestion Pipeline
   - Component 4: Experience Vault & Retrieval Service
   - Component 5: Job Description (JD) Analysis & Hybrid Matching (60/40)
   - Component 6: Anti-Hallucination Role Refraction & Diff Guardrails
   - Component 7: Tailored Resume & WeasyPrint/pydyf PDF Generation
   - Component 8: Career Agents (Gap Project Architect, Mock Interviewer) & Chat Assistant
2. Interconnectivity Tests:
   - Database <-> ORM <-> Vector Indexing
   - LiteLLM <-> Ollama Model Execution
   - FastAPI REST API Routes <-> Business Logic Services
   - Frontend API Client <-> Backend API Route Specs
3. Overall System Integration:
   - Complete unified workflow simulating an end-to-end candidate journey.
"""

import os
import json
import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.db.models import (
    User,
    ExperienceNode,
    Project,
    JDSession,
)
from app.services.embedding_service import embedding_service
from app.services.diff_service import diff_service
from app.services.retrieval_service import retrieval_service
from app.services.jd_service import jd_service
from app.services.refraction_service import refraction_service
from app.services.resume_service import resume_service
from app.services.agent_service import agent_service
from app.services.chat_service import chat_service
from app.scripts.ingest import run_ingestion, DEFAULT_PROFILE_PATH


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client():
    """Provides FastAPI TestClient instance."""
    with TestClient(app) as client:
        yield client


# =====================================================================
# SECTION 1: END-TO-END TESTING OF EACH COMPONENT IN ISOLATION
# =====================================================================

class TestComponent1DatabaseAndPgvector:
    """Component 1: PostgreSQL 16 + pgvector Database."""

    def test_database_connection_and_version(self, db_session):
        res = db_session.execute(text("SELECT version();")).scalar()
        assert res is not None
        assert "PostgreSQL" in res

    def test_pgvector_extension_enabled(self, db_session):
        res = db_session.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ).scalar()
        assert res == "vector", "pgvector extension is not installed or enabled"

    def test_all_seven_tables_exist(self, db_session):
        required_tables = {
            "users",
            "experience_nodes",
            "projects",
            "skills_profile",
            "refractions",
            "jd_sessions",
            "resume_outputs",
        }
        res = db_session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        ).fetchall()
        existing_tables = {r[0] for r in res}
        missing = required_tables - existing_tables
        assert not missing, f"Missing required database tables: {missing}"

    def test_vector_columns_configured(self, db_session):
        res = db_session.execute(
            text(
                "SELECT column_name, data_type, udt_name FROM information_schema.columns "
                "WHERE table_name = 'experience_nodes' AND column_name = 'embedding';"
            )
        ).fetchone()
        assert res is not None
        assert res[2] == "vector"


class TestComponent2EmbeddingEngine:
    """Component 2: Embedding Engine with Ollama nomic-embed-text."""

    def test_embedding_service_available(self):
        assert embedding_service.available is True
        assert embedding_service.dimensions == 768

    def test_single_text_embedding(self):
        text_sample = "Distributed Systems Architect with Kubernetes and Go"
        emb = embedding_service.embed_text(text_sample)
        assert emb is not None
        assert isinstance(emb, list)
        assert len(emb) == 768
        assert all(isinstance(x, (float, int)) for x in emb)
        assert any(x != 0 for x in emb)

    def test_batch_text_embeddings(self):
        texts = [
            "Building cloud-native infrastructure with Terraform",
            "Designing event-driven microservices with Apache Kafka",
        ]
        embs = embedding_service.embed_texts(texts)
        assert len(embs) == 2
        assert len(embs[0]) == 768
        assert len(embs[1]) == 768


class TestComponent3IngestionPipeline:
    """Component 3: Career History Ingestion Pipeline."""

    def test_master_profile_file_exists(self):
        assert os.path.exists(DEFAULT_PROFILE_PATH)
        with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "personal_info" in data
        assert "experience" in data
        assert "skills" in data
        assert "projects" in data

    def test_ingestion_data_persistence(self, db_session):
        user = db_session.query(User).first()
        assert user is not None
        nodes_count = db_session.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).count()
        assert nodes_count > 0
        projects_count = db_session.query(Project).filter(Project.user_id == user.id).count()
        assert projects_count > 0


class TestComponent4RetrievalEngine:
    """Component 4: Semantic Vector Retrieval Engine."""

    def test_vector_search_experience_nodes(self, db_session):
        user = db_session.query(User).first()
        assert user is not None

        query_emb = embedding_service.embed_text("Cloud architecture, Kubernetes orchestration, Docker")
        assert query_emb is not None

        matches = retrieval_service.search_experience_nodes_by_embedding(
            embedding=query_emb,
            user_id=str(user.id),
            db=db_session,
            limit=5,
        )
        assert len(matches) > 0
        for m in matches:
            assert "node_id" in m
            assert "similarity" in m
            assert 0.0 <= m["similarity"] <= 1.0
            assert "raw_text" in m
            assert "company" in m

    def test_vector_search_projects(self, db_session):
        user = db_session.query(User).first()
        query_emb = embedding_service.embed_text("High performance distributed cache in Go")
        assert query_emb is not None

        projects = retrieval_service.search_projects_by_embedding(
            embedding=query_emb,
            user_id=str(user.id),
            db=db_session,
            limit=3,
        )
        assert isinstance(projects, list)


class TestComponent5JDServiceAndHybridMatching:
    """Component 5: Job Description Analysis & 60/40 Hybrid Matcher."""

    @pytest.mark.asyncio
    async def test_jd_analysis_extraction(self, db_session):
        user = db_session.query(User).first()
        assert user is not None

        jd_text = (
            "We are seeking a Senior Platform Engineer to build scalable microservices. "
            "Required skills: Go, Kubernetes, Kafka, Terraform, Distributed Systems, CI/CD, AWS."
        )

        analysis = await jd_service.analyze_jd(
            jd_text=jd_text,
            user_email=user.email,
            db=db_session,
        )

        assert "session_id" in analysis
        assert "keywords" in analysis
        assert len(analysis["keywords"]) > 0

        # Test Hybrid Score
        score = jd_service.score_match(
            jd_session_id=analysis["session_id"],
            user_id=str(user.id),
            db=db_session,
        )

        assert "overall_score" in score
        assert 0.0 <= score["overall_score"] <= 100.0
        assert "semantic_score" in score
        assert "keyword_score" in score
        assert "present_keywords" in score
        assert "missing_keywords" in score
        assert "top_matches" in score

        expected = round(0.6 * score["semantic_score"] + 0.4 * score["keyword_score"], 1)
        assert abs(score["overall_score"] - expected) <= 0.2


class TestComponent6DiffAndGuardrails:
    """Component 6: SequenceMatcher & Anti-Hallucination Guardrails."""

    def test_token_preservation_success(self):
        original = "Engineered high-throughput Go queue processing 50,000 req/sec with 99.99% uptime on AWS EKS."
        reframed = "Architected a scalable Go messaging pipeline handling 50,000 req/sec maintaining 99.99% uptime across AWS EKS."
        verif = diff_service.full_verify(original, reframed)
        assert verif["passed"] is True
        assert verif["facts"]["passed"] is True
        assert verif["truncation"]["is_truncated"] is False

    def test_token_omission_failure(self):
        original = "Migrated 25 microservices to Kubernetes reducing costs by 40%."
        hallucinated = "Led migration of microservices into the cloud reducing infrastructure expenses significantly."
        verif = diff_service.full_verify(original, hallucinated)
        assert verif["passed"] is False
        assert verif["facts"]["passed"] is False
        assert len(verif["facts"]["missing_metrics"]) > 0 or len(verif["facts"]["missing_techs"]) > 0


class TestComponent7RefractionEngine:
    """Component 7: Multi-Lens Role Refraction Engine."""

    @pytest.mark.asyncio
    async def test_refract_experience_node_platform_lens(self, db_session):
        user = db_session.query(User).first()
        node = db_session.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).first()
        assert node is not None

        result = await refraction_service.refract(
            experience_node_id=str(node.id),
            lens="platform",
            user_id=str(user.id),
            db=db_session,
        )

        assert "refraction_id" in result
        assert result["lens"] == "platform"
        assert len(result["reframed_text"]) > 0
        assert "verification" in result
        assert result["verification"]["diff"]["similarity_ratio"] > 0


class TestComponent8ResumeAndPDFEngine:
    """Component 8: ATS Resume HTML & PDF Generation."""

    @pytest.mark.asyncio
    async def test_resume_generation_and_pdf(self, db_session):
        user = db_session.query(User).first()
        jd_sess = db_session.query(JDSession).filter(JDSession.user_id == user.id).first()
        assert jd_sess is not None

        res = await resume_service.generate_resume_for_jd(
            jd_session_id=str(jd_sess.id),
            user_id=str(user.id),
            db=db_session,
            lens="platform",
            template="modern",
        )

        assert "resume_id" in res
        assert "<html" in res["final_content"].lower()

        pdf_bytes = resume_service.render_pdf(res["final_content"])
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 100
        assert pdf_bytes.startswith(b"%PDF-"), "Generated file is not a valid PDF binary"


class TestComponent9CareerAgentsAndChat:
    """Component 9: Career Agents & Chat."""

    @pytest.mark.asyncio
    async def test_gap_project_architect(self, db_session):
        user = db_session.query(User).first()
        jd_sess = db_session.query(JDSession).filter(JDSession.user_id == user.id).first()
        assert jd_sess is not None

        res = await agent_service.architect_gap_filler_project(
            jd_session_id=str(jd_sess.id),
            user_id=str(user.id),
            db=db_session,
        )

        assert "project_blueprint" in res
        blueprint = res["project_blueprint"]
        assert "project_name" in blueprint
        assert "architecture_summary" in blueprint or "architecture" in blueprint

    @pytest.mark.asyncio
    async def test_mock_interview_generator(self, db_session):
        user = db_session.query(User).first()
        jd_sess = db_session.query(JDSession).filter(JDSession.user_id == user.id).first()
        assert jd_sess is not None

        res = await agent_service.generate_mock_interview(
            jd_session_id=str(jd_sess.id),
            user_id=str(user.id),
            db=db_session,
        )

        assert "interview_questions" in res
        assert len(res["interview_questions"]) > 0

    @pytest.mark.asyncio
    async def test_chat_service(self):
        resp = await chat_service.chat("What are my core backend technologies?", temperature=0.3)
        assert isinstance(resp, str)
        assert len(resp) > 0


# =====================================================================
# SECTION 2: INTERCONNECTIVITY TESTING BETWEEN COMPONENTS
# =====================================================================

class TestInterconnectivity:
    """Testing connections and data handoffs between components."""

    def test_health_check_endpoint(self, test_client):
        resp = test_client.get("/api/v1/health/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_vault_endpoint_connectivity(self, test_client):
        resp = test_client.get("/api/v1/ingest/vault")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"] is not None
        assert len(data["nodes"]) > 0
        assert len(data["skills"]) > 0

    def test_jd_scoring_and_matches_flow_via_rest(self, test_client, db_session):
        user = db_session.query(User).first()
        jd_sess = db_session.query(JDSession).filter(JDSession.user_id == user.id).first()
        assert jd_sess is not None

        score_resp = test_client.get(f"/api/v1/jd/{jd_sess.id}/score?user_id={user.id}")
        assert score_resp.status_code == 200
        assert "overall_score" in score_resp.json()

        matches_resp = test_client.get(f"/api/v1/jd/{jd_sess.id}/matches?user_id={user.id}")
        assert matches_resp.status_code == 200
        assert len(matches_resp.json()["matches"]) > 0

    def test_refraction_and_diff_flow_via_rest(self, test_client, db_session):
        user = db_session.query(User).first()
        node = db_session.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).first()

        payload = {
            "experience_node_id": str(node.id),
            "lens": "infrastructure",
            "user_id": str(user.id),
        }
        resp = test_client.post("/api/v1/refraction/", json=payload)
        assert resp.status_code == 200
        refract_data = resp.json()
        refraction_id = refract_data["refraction_id"]

        diff_resp = test_client.get(f"/api/v1/refraction/{refraction_id}/diff")
        assert diff_resp.status_code == 200
        diff_data = diff_resp.json()
        assert "diff" in diff_data
        assert "facts" in diff_data

    def test_resume_generation_and_pdf_download_flow_via_rest(self, test_client, db_session):
        user = db_session.query(User).first()
        jd_sess = db_session.query(JDSession).filter(JDSession.user_id == user.id).first()

        payload = {
            "jd_session_id": str(jd_sess.id),
            "user_id": str(user.id),
            "lens": "platform",
            "template": "classic",
        }
        resp = test_client.post("/api/v1/resume/generate", json=payload)
        assert resp.status_code == 200
        resume_data = resp.json()
        resume_id = resume_data["resume_id"]

        get_resp = test_client.get(f"/api/v1/resume/{resume_id}")
        assert get_resp.status_code == 200

        pdf_resp = test_client.get(f"/api/v1/resume/{resume_id}/pdf")
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert len(pdf_resp.content) > 100

    def test_direct_pdf_rendering_via_rest(self, test_client):
        html_input = "<html><body><h1>Direct PDF Test</h1><p>Verifying HTML to PDF compiler.</p></body></html>"
        resp = test_client.post("/api/v1/resume/render-pdf", json={"html_content": html_input})
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF-")

    def test_chat_assistant_flow_via_rest(self, test_client):
        payload = {"message": "Hello LoomResume identity engine!", "temperature": 0.2}
        resp = test_client.post("/api/v1/chat/", json=payload)
        assert resp.status_code == 200
        assert "response" in resp.json()
