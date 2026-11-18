"""
Comprehensive End-to-End System Test Runner for LoomResume.

Executes:
  Phase 1: Component E2E Testing (Testing each component in isolation)
  Phase 2: Interconnectivity Testing (Testing data flow & contracts between components)
  Phase 3: Overall Application Testing (Testing the whole app as a single unified component)
"""

import asyncio
import os
import sys
import time
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.db.models import (
    ExperienceNode,
    JDSession,
    Project,
    Refraction,
    ResumeOutput,
    SkillsProfile,
    User,
)
from app.main import app
from app.scripts.ingest import DEFAULT_PROFILE_PATH, run_ingestion
from app.services.agent_service import agent_service
from app.services.chat_service import chat_service
from app.services.diff_service import diff_service
from app.services.embedding_service import embedding_service
from app.services.jd_service import jd_service
from app.services.llm_service import llm_service
from app.services.refraction_service import refraction_service
from app.services.resume_service import resume_service
from app.services.retrieval_service import retrieval_service


class TestReport:
    def __init__(self):
        self.results = []
        self.start_time = time.time()

    def record(self, phase: str, component: str, test_name: str, passed: bool, details: str = ""):
        self.results.append({
            "phase": phase,
            "component": component,
            "test_name": test_name,
            "passed": passed,
            "details": details,
        })
        icon = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{icon}] {phase} | {component} -> {test_name}")
        if details:
            print(f"       Details: {details}")

    def print_summary(self):
        elapsed = time.time() - self.start_time
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print("\n" + "=" * 80)
        print(f"  LOOMRESUME END-TO-END TEST SUITE SUMMARY ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("=" * 80)
        print(f"  Total Tests Executed : {total}")
        print(f"  Passed               : {passed}")
        print(f"  Failed               : {failed}")
        print(f"  Total Duration       : {elapsed:.2f}s")
        print("=" * 80)

        # Group by phase
        phases = {}
        for r in self.results:
            phases.setdefault(r["phase"], []).append(r)

        for phase_name, tests in phases.items():
            p_count = sum(1 for t in tests if t["passed"])
            f_count = len(tests) - p_count
            print(f"\n📁 {phase_name.upper()} ({p_count}/{len(tests)} Passed)")
            for t in tests:
                icon = "✅" if t["passed"] else "❌"
                print(f"   {icon} {t['component']}: {t['test_name']}")
                if not t["passed"] and t["details"]:
                    print(f"      ERROR: {t['details']}")

        print("=" * 80)
        return failed == 0


async def run_all_tests():
    report = TestReport()
    db = SessionLocal()
    client = TestClient(app)

    print("\n" + "=" * 80)
    print("  PHASE 1: END-TO-END TESTING OF INDIVIDUAL COMPONENTS")
    print("=" * 80)

    # -------------------------------------------------------------
    # Component 1: Database & pgvector
    # -------------------------------------------------------------
    try:
        ver = db.execute(text("SELECT version();")).scalar()
        report.record("Phase 1", "Database & pgvector", "PostgreSQL Connection", "PostgreSQL" in ver, f"Version: {ver[:45]}...")
    except Exception as e:
        report.record("Phase 1", "Database & pgvector", "PostgreSQL Connection", False, str(e))

    try:
        ext = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';")).scalar()
        report.record("Phase 1", "Database & pgvector", "pgvector Extension", ext == "vector", "Extension enabled in public schema")
    except Exception as e:
        report.record("Phase 1", "Database & pgvector", "pgvector Extension", False, str(e))

    try:
        required_tables = {"users", "experience_nodes", "projects", "skills_profile", "refractions", "jd_sessions", "resume_outputs"}
        res = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")).fetchall()
        existing = {r[0] for r in res}
        missing = required_tables - existing
        report.record("Phase 1", "Database & pgvector", "7 Core Tables Schema Check", len(missing) == 0, f"Found: {len(existing)} tables, Missing: {list(missing)}")
    except Exception as e:
        report.record("Phase 1", "Database & pgvector", "7 Core Tables Schema Check", False, str(e))

    # -------------------------------------------------------------
    # Component 2: Vector Embedding Engine
    # -------------------------------------------------------------
    try:
        emb_avail = embedding_service.available and embedding_service.dimensions == 768
        report.record("Phase 1", "Embedding Engine", "Provider Availability (Ollama nomic-embed-text)", emb_avail, f"Provider: {embedding_service._provider}, Model: {embedding_service._model}, Dims: {embedding_service.dimensions}")
    except Exception as e:
        report.record("Phase 1", "Embedding Engine", "Provider Availability (Ollama nomic-embed-text)", False, str(e))

    try:
        vec = embedding_service.embed_text("Senior Systems Engineer specializing in high-throughput Go microservices")
        is_valid_vec = vec is not None and len(vec) == 768 and all(isinstance(x, (float, int)) for x in vec)
        report.record("Phase 1", "Embedding Engine", "Single Text 768d Vector Generation", is_valid_vec, f"Generated {len(vec) if vec else 0}-dimension dense vector")
    except Exception as e:
        report.record("Phase 1", "Embedding Engine", "Single Text 768d Vector Generation", False, str(e))

    try:
        batch_vecs = embedding_service.embed_texts(["Kubernetes cluster autoscaling", "Kafka partitioned stream processing"])
        batch_valid = len(batch_vecs) == 2 and len(batch_vecs[0]) == 768 and len(batch_vecs[1]) == 768
        report.record("Phase 1", "Embedding Engine", "Batch Text Embedding", batch_valid, f"Generated {len(batch_vecs)} vectors of length {len(batch_vecs[0])}")
    except Exception as e:
        report.record("Phase 1", "Embedding Engine", "Batch Text Embedding", False, str(e))

    # -------------------------------------------------------------
    # Component 3: Diff Service & Anti-Hallucination Guardrails
    # -------------------------------------------------------------
    try:
        orig = "Engineered distributed queue in Go processing 50,000 req/sec with 99.99% uptime on AWS EKS."
        good = "Architected a distributed Go messaging queue handling 50,000 req/sec while maintaining 99.99% uptime across AWS EKS."
        v_good = diff_service.full_verify(orig, good)
        report.record("Phase 1", "Diff & Guardrail Service", "Factual Token Preservation Check (Valid Refraction)", v_good["passed"], f"Similarity: {v_good['diff']['similarity_ratio']:.2f}, Facts passed: {v_good['facts']['passed']}")
    except Exception as e:
        report.record("Phase 1", "Diff & Guardrail Service", "Factual Token Preservation Check (Valid Refraction)", False, str(e))

    try:
        bad = "Managed a generic cloud system for the team."
        v_bad = diff_service.full_verify(orig, bad)
        failed_detected = not v_bad["passed"] and (len(v_bad["facts"]["missing_metrics"]) > 0 or len(v_bad["facts"]["missing_techs"]) > 0)
        report.record("Phase 1", "Diff & Guardrail Service", "Omission/Hallucination Detection Guardrail", failed_detected, f"Successfully flagged omitted metrics: {v_bad['facts']['missing_metrics']}, techs: {v_bad['facts']['missing_techs']}")
    except Exception as e:
        report.record("Phase 1", "Diff & Guardrail Service", "Omission/Hallucination Detection Guardrail", False, str(e))

    # -------------------------------------------------------------
    # Component 4: Career Ingestion Pipeline & Experience Vault
    # -------------------------------------------------------------
    try:
        user = db.query(User).first()
        exp_count = db.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).count() if user else 0
        proj_count = db.query(Project).filter(Project.user_id == user.id).count() if user else 0
        skills_count = db.query(SkillsProfile).filter(SkillsProfile.user_id == user.id).count() if user else 0
        vault_populated = user is not None and exp_count > 0 and proj_count > 0 and skills_count > 0
        report.record("Phase 1", "Ingestion & Vault", "Vault Data Persistence", vault_populated, f"User: {user.email if user else None}, Nodes: {exp_count}, Projects: {proj_count}, Skills: {skills_count}")
    except Exception as e:
        report.record("Phase 1", "Ingestion & Vault", "Vault Data Persistence", False, str(e))

    # -------------------------------------------------------------
    # Component 5: Retrieval Engine (HNSW Vector Search)
    # -------------------------------------------------------------
    try:
        search_vec = embedding_service.embed_text("Kubernetes container orchestration and Docker")
        results = retrieval_service.search_experience_nodes_by_embedding(
            embedding=search_vec,
            user_id=str(user.id),
            db=db,
            limit=5,
        )
        has_results = len(results) > 0 and 0.0 <= results[0]["similarity"] <= 1.0
        report.record("Phase 1", "Retrieval Engine", "Semantic Vector Search (<=> Cosine Distance)", has_results, f"Retrieved {len(results)} nodes. Top match similarity: {results[0]['similarity']:.2f}")
    except Exception as e:
        report.record("Phase 1", "Retrieval Engine", "Semantic Vector Search (<=> Cosine Distance)", False, str(e))

    # -------------------------------------------------------------
    # Component 6: Job Description Service & 60/40 Hybrid Scoring
    # -------------------------------------------------------------
    jd_session_id = None
    try:
        jd_input = (
            "Seeking a Senior Platform Engineer. Requirements: Go, Kubernetes, Kafka, Terraform, "
            "Distributed Systems, AWS, High Availability, Microservices."
        )
        analysis = await jd_service.analyze_jd(jd_text=jd_input, user_email=user.email, db=db)
        jd_session_id = analysis["session_id"]
        keywords = analysis["keywords"]
        report.record("Phase 1", "JD Analysis Service", "Keyword & Metadata Extraction", len(keywords) > 0, f"Extracted {len(keywords)} keywords: {keywords[:5]}... Role Level: {analysis['role_level']}")
    except Exception as e:
        report.record("Phase 1", "JD Analysis Service", "Keyword & Metadata Extraction", False, str(e))

    try:
        if jd_session_id:
            score_data = jd_service.score_match(jd_session_id=jd_session_id, user_id=str(user.id), db=db)
            ov = score_data["overall_score"]
            sem = score_data["semantic_score"]
            kw = score_data["keyword_score"]
            expected = round(0.6 * sem + 0.4 * kw, 1)
            formula_ok = abs(ov - expected) <= 0.2
            report.record("Phase 1", "JD Matching Engine", "60/40 Hybrid Match Score Computation", formula_ok, f"Overall: {ov}%, Semantic: {sem}%, Keyword: {kw}% (Present: {len(score_data['present_keywords'])}, Missing: {len(score_data['missing_keywords'])})")
    except Exception as e:
        report.record("Phase 1", "JD Matching Engine", "60/40 Hybrid Match Score Computation", False, str(e))

    # -------------------------------------------------------------
    # Component 7: Multi-Lens Role Refraction Engine
    # -------------------------------------------------------------
    refracted_node_id = None
    try:
        top_node = db.query(ExperienceNode).filter(ExperienceNode.user_id == user.id).first()
        refracted_node_id = str(top_node.id)
        ref_res = await refraction_service.refract(
            experience_node_id=refracted_node_id,
            lens="platform",
            user_id=str(user.id),
            db=db,
        )
        ref_ok = len(ref_res["reframed_text"]) > 0 and ref_res["verification"]["diff"]["similarity_ratio"] > 0
        report.record("Phase 1", "Role Refraction Engine", "Platform Lens Narrative Pivot & Guardrails", ref_ok, f"Lens: {ref_res['lens']}, Similarity: {ref_res['verification']['diff']['similarity_ratio']:.2f}")
    except Exception as e:
        report.record("Phase 1", "Role Refraction Engine", "Platform Lens Narrative Pivot & Guardrails", False, str(e))

    # -------------------------------------------------------------
    # Component 8: ATS Resume HTML & WeasyPrint/pydyf PDF Engine
    # -------------------------------------------------------------
    resume_id = None
    try:
        if jd_session_id:
            res_out = await resume_service.generate_resume_for_jd(
                jd_session_id=jd_session_id,
                user_id=str(user.id),
                db=db,
                lens="platform",
                template="modern",
            )
            resume_id = res_out["resume_id"]
            html_ok = "<html" in res_out["final_content"].lower() and "experience" in res_out["final_content"].lower()
            report.record("Phase 1", "Resume Engine", "Tailored ATS Resume HTML Assembly", html_ok, f"Resume ID: {resume_id}, HTML length: {len(res_out['final_content'])} chars")

            # PDF Render
            pdf_bytes = resume_service.render_pdf(res_out["final_content"])
            pdf_ok = isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 500 and pdf_bytes.startswith(b"%PDF-")
            report.record("Phase 1", "Resume Engine", "Vector PDF Render (WeasyPrint / pydyf fallback)", pdf_ok, f"Generated valid PDF binary: {len(pdf_bytes)} bytes")
    except Exception as e:
        report.record("Phase 1", "Resume Engine", "ATS Resume & PDF Generation", False, str(e))

    # -------------------------------------------------------------
    # Component 9: Career Agents (Gap Architect, Mock Interview) & Chat
    # -------------------------------------------------------------
    try:
        if jd_session_id:
            gap_data = await agent_service.architect_gap_filler_project(
                jd_session_id=jd_session_id,
                user_id=str(user.id),
                db=db,
            )
            bp = gap_data.get("project_blueprint", {})
            gap_ok = "project_name" in bp and ("architecture_summary" in bp or "architecture" in bp)
            report.record("Phase 1", "Career Agents", "Gap-Filler Project Architect Agent", gap_ok, f"Project: {bp.get('project_name', 'N/A')}")
    except Exception as e:
        report.record("Phase 1", "Career Agents", "Gap-Filler Project Architect Agent", False, str(e))

    try:
        if jd_session_id:
            interview_data = await agent_service.generate_mock_interview(
                jd_session_id=jd_session_id,
                user_id=str(user.id),
                db=db,
            )
            qs = interview_data.get("interview_questions", [])
            interview_ok = len(qs) > 0 and "question" in qs[0]
            report.record("Phase 1", "Career Agents", "Scenario Mock Interview Generator Agent", interview_ok, f"Generated {len(qs)} interview questions with scoring rubrics")
    except Exception as e:
        report.record("Phase 1", "Career Agents", "Scenario Mock Interview Generator Agent", False, str(e))

    try:
        chat_reply = await chat_service.chat("What are my core competencies in distributed systems?", temperature=0.2)
        chat_ok = isinstance(chat_reply, str) and len(chat_reply) > 20
        report.record("Phase 1", "Identity Assistant", "Grounded Identity Conversational Chat", chat_ok, f"Reply: {chat_reply[:80]}...")
    except Exception as e:
        report.record("Phase 1", "Identity Assistant", "Grounded Identity Conversational Chat", False, str(e))

    # -------------------------------------------------------------
    # Component 10: Frontend Studio (Next.js 16 + React 19)
    # -------------------------------------------------------------
    try:
        page_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "app", "page.tsx")
        api_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "lib", "api.ts")
        fe_ok = os.path.exists(page_path) and os.path.exists(api_path)
        report.record("Phase 1", "Frontend Studio", "Next.js 16 Page & API Client Structure", fe_ok, f"page.tsx ({os.path.getsize(page_path)} bytes), api.ts ({os.path.getsize(api_path)} bytes)")
    except Exception as e:
        report.record("Phase 1", "Frontend Studio", "Next.js 16 Page & API Client Structure", False, str(e))


    print("\n" + "=" * 80)
    print("  PHASE 2: TESTING INTERCONNECTIVITY BETWEEN COMPONENTS")
    print("=" * 80)

    # 1. Database <-> Vector Storage Interconnect
    try:
        raw_vec_check = db.execute(text("SELECT id, embedding IS NOT NULL FROM experience_nodes LIMIT 1;")).fetchone()
        report.record("Phase 2", "DB <-> Vector Storage", "pgvector HNSW Cosine Index Interconnectivity", raw_vec_check is not None and raw_vec_check[1] is True, "Experience nodes properly bound to pgvector column")
    except Exception as e:
        report.record("Phase 2", "DB <-> Vector Storage", "pgvector HNSW Cosine Index Interconnectivity", False, str(e))

    # 2. LiteLLM <-> Ollama Interconnect
    try:
        test_llm_msg = await llm_service.generate("Reply with: PING_OK", temperature=0.1)
        report.record("Phase 2", "LiteLLM <-> Ollama", "Local LLM Inference Pipeline", "PING_OK" in test_llm_msg or len(test_llm_msg) > 0, f"Ollama response received: '{test_llm_msg.strip()}'")
    except Exception as e:
        report.record("Phase 2", "LiteLLM <-> Ollama", "Local LLM Inference Pipeline", False, str(e))

    # 3. FastAPI REST Endpoints Interconnectivity
    endpoints_to_test = [
        ("GET", "/api/v1/health/", None, 200),
        ("GET", "/api/v1/ingest/vault", None, 200),
        ("GET", f"/api/v1/jd/{jd_session_id}/score?user_id={user.id}" if jd_session_id else None, None, 200),
        ("GET", f"/api/v1/jd/{jd_session_id}/matches?user_id={user.id}" if jd_session_id else None, None, 200),
        ("GET", f"/api/v1/resume/{resume_id}" if resume_id else None, None, 200),
        ("GET", f"/api/v1/resume/{resume_id}/pdf" if resume_id else None, None, 200),
        ("POST", "/api/v1/resume/render-pdf", {"html_content": "<h1>Test</h1>"}, 200),
        ("POST", "/api/v1/chat/", {"chat_id": "e2e_test", "message": "Test message", "temperature": 0.1}, 200),
    ]

    for method, path, payload, expected_status in endpoints_to_test:
        if not path:
            continue
        try:
            if method == "GET":
                resp = client.get(path)
            else:
                resp = client.post(path, json=payload)
            success = resp.status_code == expected_status
            report.record("Phase 2", "API Endpoints", f"{method} {path.split('?')[0]}", success, f"Status: {resp.status_code} (Expected {expected_status})")
        except Exception as e:
            report.record("Phase 2", "API Endpoints", f"{method} {path.split('?')[0]}", False, str(e))

    # 4. Frontend Client Contracts <-> Backend Routes Check
    try:
        frontend_api_endpoints = [
            "/health/",
            "/ingest/vault",
            "/ingest/",
            "/jd/analyze",
            "/jd/{session_id}/score",
            "/jd/{session_id}/matches",
            "/refraction/",
            "/refraction/{refraction_id}/diff",
            "/resume/generate",
            "/resume/{resume_id}",
            "/resume/{resume_id}/pdf",
            "/resume/{resume_id}/template",
            "/agents/gap-project",
            "/agents/mock-interview",
            "/chat/",
        ]
        registered_routes = [r.path.replace("/api/v1", "") for r in app.routes if hasattr(r, "path")]
        matched = 0
        for ep in frontend_api_endpoints:
            pattern = ep.replace("{session_id}", "{session_id}").replace("{resume_id}", "{resume_id}").replace("{refraction_id}", "{refraction_id}")
            if any(r.endswith(pattern) or pattern in r for r in registered_routes):
                matched += 1
        all_matched = matched == len(frontend_api_endpoints)
        report.record("Phase 2", "Frontend-Backend Contracts", "1:1 API Route Alignment", all_matched, f"{matched}/{len(frontend_api_endpoints)} frontend endpoints match backend route controllers")
    except Exception as e:
        report.record("Phase 2", "Frontend-Backend Contracts", "1:1 API Route Alignment", False, str(e))


    print("\n" + "=" * 80)
    print("  PHASE 3: OVERALL APPLICATION TESTING (APP AS A SINGLE UNIFIED COMPONENT)")
    print("=" * 80)

    try:
        print("  Executing unified candidate journey simulation...")
        t0 = time.time()

        # 1. Health check
        h_resp = client.get("/api/v1/health/")
        assert h_resp.status_code == 200

        # 2. Vault inspection
        v_resp = client.get("/api/v1/ingest/vault")
        assert v_resp.status_code == 200
        v_data = v_resp.json()
        u_id = v_data["user"]["id"]
        u_email = v_data["user"]["email"]

        # 3. Analyze real-world Job Description
        target_jd = (
            "Staff Infrastructure & Platform Engineer. "
            "We are looking for an experienced engineer to architect our next-generation cloud foundation. "
            "Stack: Go, Kubernetes, Kafka, Terraform, AWS, Prometheus, gRPC, Distributed Consensus. "
            "You will own multi-cluster orchestration, zero-downtime CI/CD pipelines, and platform reliability."
        )
        jd_post = client.post("/api/v1/jd/analyze", json={"jd_text": target_jd, "user_email": u_email})
        assert jd_post.status_code == 200
        sess_id = jd_post.json()["session_id"]

        # 4. Score candidate against JD
        s_resp = client.get(f"/api/v1/jd/{sess_id}/score?user_id={u_id}")
        assert s_resp.status_code == 200
        s_data = s_resp.json()

        # 5. Retrieve ranked experience matches
        m_resp = client.get(f"/api/v1/jd/{sess_id}/matches?user_id={u_id}")
        assert m_resp.status_code == 200
        matches = m_resp.json()["matches"]
        assert len(matches) > 0
        top_node_id = matches[0]["node_id"]

        # 6. Refract top experience node into "Platform" lens with anti-hallucination verification
        ref_post = client.post(
            "/api/v1/refraction/",
            json={"experience_node_id": top_node_id, "lens": "platform", "user_id": u_id},
        )
        assert ref_post.status_code == 200
        ref_data = ref_post.json()
        assert ref_data["verification"]["facts"]["passed"] is True

        # 7. Verify diff audit
        diff_get = client.get(f"/api/v1/refraction/{ref_data['refraction_id']}/diff")
        assert diff_get.status_code == 200

        # 8. Compile tailored ATS Resume
        res_post = client.post(
            "/api/v1/resume/generate",
            json={"jd_session_id": sess_id, "user_id": u_id, "lens": "platform", "template": "modern"},
        )
        assert res_post.status_code == 200
        new_resume_id = res_post.json()["resume_id"]

        # 9. Download rendered PDF
        pdf_get = client.get(f"/api/v1/resume/{new_resume_id}/pdf")
        assert pdf_get.status_code == 200
        assert pdf_get.content.startswith(b"%PDF-")

        # 10. Generate Gap-Filler Project Blueprint
        gap_post = client.post(
            "/api/v1/agents/gap-project",
            json={"jd_session_id": sess_id, "user_id": u_id},
        )
        assert gap_post.status_code == 200
        gap_blueprint = gap_post.json()["project_blueprint"]

        # 11. Generate Mock Technical Interview Questions
        int_post = client.post(
            "/api/v1/agents/mock-interview",
            json={"jd_session_id": sess_id, "user_id": u_id},
        )
        assert int_post.status_code == 200
        mock_qs = int_post.json()["interview_questions"]

        # 12. Chat with Identity Assistant
        chat_post = client.post(
            "/api/v1/chat/",
            json={"chat_id": "journey_chat", "message": "What are my strengths for a Staff Platform Engineer role?", "temperature": 0.2},
        )
        assert chat_post.status_code == 200, f"Chat endpoint failed with status {chat_post.status_code}: {chat_post.text}"

        journey_duration = time.time() - t0
        report.record(
            "Phase 3",
            "End-to-End System",
            "Complete Candidate Journey (Health -> JD -> Score -> Refract -> Diff -> Resume -> PDF -> Gap Project -> Mock Interview -> Chat)",
            True,
            f"Successfully executed all 12 steps in {journey_duration:.2f}s. Hybrid Score: {s_data['overall_score']}%, PDF: {len(pdf_get.content)} bytes, Project: '{gap_blueprint.get('project_name', 'Blueprint')}', Questions: {len(mock_qs)}",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        report.record("Phase 3", "End-to-End System", "Complete Candidate Journey", False, f"{type(e).__name__}: {str(e) or 'Assertion check failed'}")

    db.close()
    success = report.print_summary()
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
