# LoomResume: The Cross-Functional Impact Engine

**LoomResume** is an AI-powered professional identity platform that treats your career history as a living database. It "refracts" your raw experiences into high-impact narratives tailored for specific job roles (Backend, Infra, Manager, etc.) and generates evidence-based projects to fill skill gaps.

## 🚀 Core Features
- **The Experience Vault:** A RAG-based persistent store for every project, metric, and skill you've ever mastered.
- **Role Refraction:** Automatically pivots a single technical achievement into multiple narratives (e.g., Business Impact, Infrastructure Stability, or Team Leadership).
- **JD Contextualization:** Analyzes Job Descriptions to select and rephrase the most relevant points from your history.
- **Gap-Filler Projects:** Proactively suggests and architects projects to bridge the gap between your current skills and your target roles.

## 🛠 Tech Stack
- **Orchestration:** LangChain / LangGraph
- **LLM Engine:** Ollama (Local) / GPT-4o (Production)
- **Vector Database:** PostgreSQL with `pgvector`
- **Observability:** LangSmith
- **Frontend:** Chat-first interface (Next.js/Tailwind)
- **Formatting:** LaTeX (PDF), Markdown (READMEs)

## � Database Migrations
This repo uses ordered SQL migration scripts in `migrations/` to define the core schema and indexes.

Alembic is also configured for SQLAlchemy-based schema management.
- `alembic.ini` and `alembic/env.py` are set up to use `app.core.config.settings.SQLALCHEMY_DATABASE_URL`.
- `alembic` reads model metadata from `app.db.models.Base.metadata`.

Example commands:
```bash
python -m pip install -e .[dev]
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic history --verbose
```

If you want to keep the existing SQL path, continue to apply `migrations/*.sql` in numeric order.

## 🗺 Roadmap
- [ ] **Phase 1:** Core RAG & Experience Node Extraction.
- [ ] **Phase 2:** JD Keyword Matching & PDF Generation.
- [ ] **Phase 3:** Market-Based Gap Analysis.
- [ ] **Phase 4:** High-Signal Project Architecting & Mock Interviewing.

## 🤝 Contributing
This is an "Outcome-First" career tool. Contributions should focus on narrative accuracy and technical depth.

## Notes for dev:
    to run
        python -m uvicorn app.main:app --reload