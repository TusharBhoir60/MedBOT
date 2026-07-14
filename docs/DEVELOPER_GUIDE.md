# Developer Guide

Welcome to the AarogyaAgent v2 developer documentation. This guide explains our conventions, how to run the project locally, and how to extend its capabilities.

## 1. Project Setup

**Prerequisites:**
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- An OpenAI API Key

**Local Bootstrapping:**
1. Clone the repository.
2. In `backend/`, copy `.env.example` to `.env`. Set `OPENAI_API_KEY`.
3. In `frontend/`, copy `.env.example` to `.env`.
4. Run `docker-compose -f docker-compose.prod.yml up --build` to verify containerized execution, OR follow the manual setup in the README.

## 2. Folder & Naming Conventions
- **Python:** Use `snake_case` for variables/functions, `PascalCase` for classes. Enforced via Ruff.
- **TypeScript:** Use `camelCase` for variables, `PascalCase` for React components.
- **Tests:** All test files must begin with `test_`.
- **API Responses:** All API JSON responses are automatically serialized to `camelCase` to match frontend TypeScript conventions. Use `pydantic.alias_generator` for this.

## 3. Extending the Application

### Adding a new LangGraph Agent
1. Create `backend/ai_engine/agents/new_agent.py`.
2. Inherit from `BaseAgent` if applicable, or define an async `invoke(state: SharedState)` function.
3. The agent **must** extract its inputs from the state, process them via the LLM, and return a dictionary of state updates.
4. If it generates confidence, it must return a `ConfidenceSchema` object mapping.
5. Register the node in `backend/ai_engine/workflow.py` using `workflow.add_node("new_agent", run_new_agent)`.

### Adding a new API Endpoint
1. Define Pydantic schemas in `backend/schemas/`.
2. Add router logic in `backend/api/v1/`.
3. Inject the required services using FastAPI `Depends`.
4. Add the router to `main.py` if it's a new domain.

### Modifying the Database
1. Update SQLAlchemy models in `backend/database/models/`.
2. Run `alembic revision --autogenerate -m "description"`.
3. Verify the generated migration in `backend/alembic/versions/`.
4. Run `alembic upgrade head`.

## 4. Testing Principles
- **100% Pass Rate:** The main branch will reject PRs with failing tests.
- **Test Isolation:** Backend tests use a SQLite SAVEPOINT strategy. Do not call `session.commit()` inside tests unless explicitly testing transaction behavior. Rely on the `db_session` fixture to auto-rollback.
- **Mocking:** External network calls (OpenAI, ChromaDB) must be mocked using `pytest.MonkeyPatch` during unit/integration tests to prevent flaky network failures.

## 5. Architectural Principles
- **Decoupling:** The Frontend and Backend share no state except through explicitly defined API contracts.
- **Fail Closed:** If the AI engine is unsure, it must gracefully degrade to `handoff` (Human-in-the-Loop) rather than hallucinating a diagnosis.

## 6. Troubleshooting

**"database is locked" during Pytest:**
This indicates a transaction collision. Ensure you are using the `db_session` fixture and that you haven't opened a separate async engine connection manually within a test. All connections must go through the monkeypatched `async_session_factory`.

**Alembic out of sync:**
If you see `Target database is not up to date`, you may have switched branches. Run `alembic downgrade base` and then `alembic upgrade head` to rebuild the schema locally, or simply delete your `medbot.db` SQLite file and run migrations from scratch.

**Docker Port Collisions:**
FastAPI binds to port `8000` and Next.js binds to `3000`. If you encounter `bind: address already in use`, ensure no local instances of Node or Uvicorn are running before executing `docker-compose up`.
