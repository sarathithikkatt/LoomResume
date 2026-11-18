# LoomResume: The Cross-Functional Impact Engine

**LoomResume** is an AI-powered professional identity platform that treats your career history as a living database. It "refracts" your raw experiences into high-impact narratives tailored for specific job roles (Platform, Infrastructure, Leadership, Business Impact, Data Engineering, Security) and generates evidence-based projects to fill skill gaps.

## 🚀 Core Features
- **The Experience Vault:** A RAG-based persistent store for every project, metric, and skill you've ever mastered with pgvector embeddings.
- **Role Refraction with Anti-Hallucination Guardrails:** Automatically pivots a single technical achievement across 6 distinct lenses with strict factual token verification (`SequenceMatcher`) and automated retries.
- **JD Contextualization & Hybrid Matching:** Analyzes Job Descriptions to extract technical keywords, computing a hybrid match score (60% vector semantic similarity + 40% lexical/ATS keyword overlap).
- **Tailored Resume & PDF Generation:** Assembles matching refracted bullets, projects, and skills into ATS-optimized HTML and renders downloadable PDF resumes via WeasyPrint (with pure-Python fallback).
- **Gap-Filler Projects & Mock Interviews:** Proactively architects production-grade projects bridging missing skill sets and generates scenario-based technical interview questions.

## 🛠 Tech Stack
- **Framework:** FastAPI, Uvicorn, Pydantic v2
- **LLM Engine:** LiteLLM (Ollama `llama3.1:8b` locally, or `gpt-4o`, Claude, Grok)
- **Vector Database:** PostgreSQL with `pgvector` (HNSW indexing)
- **Database ORM & Migrations:** SQLAlchemy 2.0 & Alembic / SQL scripts
- **PDF Rendering:** WeasyPrint + pydyf fallback
- **Testing & Quality:** Pytest, pytest-asyncio, Ruff, Black, Mypy

## 📡 API Endpoints

### Ingestion & Career Vault
* `POST /api/v1/ingest/` — Ingest `master_profile.json`, chunk experience bullets, and seed vector embeddings.

### Job Description (JD) Analysis & Matching
* `POST /api/v1/jd/analyze` — Extract structured keywords, seniority, domain, and compute JD vector embedding.
* `GET /api/v1/jd/{session_id}/score` — Hybrid match score, present vs. missing keyword gap breakdown.
* `GET /api/v1/jd/{session_id}/matches` — Ranked experience nodes matching the JD.

### Role Refraction (Anti-Hallucination)
* `POST /api/v1/refraction/` — Refract single experience node through a lens (`platform`, `infrastructure`, `leadership`, `business_impact`, `data_engineering`, `security`).
* `POST /api/v1/refraction/jd/{session_id}` — Batch refract top matched nodes for a target JD.
* `GET /api/v1/refraction/{refraction_id}/diff` — Audit diff, truncation check, and factual token preservation.

### Resume & PDF Export
* `POST /api/v1/resume/generate` — Compile a tailored resume from JD matches and refractions.
* `GET /api/v1/resume/{resume_id}` — Fetch stored resume HTML content.
* `GET /api/v1/resume/{resume_id}/pdf` — Download the compiled resume as a PDF.
* `POST /api/v1/resume/render-pdf` — Directly render any resume HTML into PDF bytes.

### Agents & Career Advising
* `POST /api/v1/agents/gap-project` — Architect a production-grade gap-filler project addressing missing JD skills.
* `POST /api/v1/agents/mock-interview` — Generate scenario-based technical interview questions.
* `POST /api/v1/chat/` — Conversational assistant with Loom identity context.

## 🗄️ Database Migrations
This repo includes 10 ordered SQL migration scripts in `migrations/` to define the core schema and indexes.

Alembic is also configured for SQLAlchemy-based schema management:
```bash
python -m pip install -e .[dev]
alembic upgrade head
```

## 🧪 Testing & Execution

Run unit tests:
```bash
pytest
```

Run dev server:
```bash
python -m uvicorn app.main:app --reload
```

## 🗺 Roadmap
- [x] **Phase 1:** Core RAG & Experience Node Extraction.
- [x] **Phase 2:** JD Keyword Matching, Role Refraction & PDF Generation.
- [x] **Phase 3:** Market-Based Gap Analysis & Gap-Filler Project Architecting.
- [x] **Phase 4:** Mock Interview Generation.
- [ ] **Phase 5:** Chat-first frontend interface (Next.js/Tailwind).
