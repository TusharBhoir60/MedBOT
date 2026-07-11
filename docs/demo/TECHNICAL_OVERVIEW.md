# Technical Overview Handout

**Project:** AarogyaAgent v2
**Type:** Full-Stack AI Healthcare Application
**Status:** v1.0.0 (Production Ready)

## Core Stack
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, shadcn/ui.
- **Backend:** FastAPI, Python 3.12, SQLAlchemy (Async), PostgreSQL.
- **AI Engine:** LangGraph, LangChain, OpenAI, ChromaDB (RAG).
- **DevOps:** Docker, GitHub Actions, Playwright, Pytest.

## Architectural Highlights
1. **Decoupled Client-Server:** Next.js UI communicates with the FastAPI backend via a secured REST API utilizing JWT Bearer authentication.
2. **LangGraph State Machine:** The AI is not a single prompt, but a cyclic graph of specialized agents (Intake, Symptom, Diagnosis). This guarantees deterministic execution paths.
3. **RAG Pipeline:** Integrates ChromaDB to retrieve authoritative medical documents, mitigating LLM hallucination risks.
4. **Test-Driven:** The backend maintains 100% test coverage using advanced `pytest-asyncio` database rollback strategies.

## GitHub Repository
*(Insert GitHub Link Here)*

## Quick Start
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```
