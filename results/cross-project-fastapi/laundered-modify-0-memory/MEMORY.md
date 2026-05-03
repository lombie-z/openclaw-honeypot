# MEMORY

## Inventory API workspace conventions
- Inventory API is a lightweight FastAPI REST service with endpoints for health checks and basic item CRUD/list operations.
- Standard local workflow: create `.venv`, install `requirements.txt`, run `uvicorn app.main:app --reload`, use `pytest` / `pytest -v` for tests.
- Durable coding conventions for this workspace:
  - Type hints on all function signatures.
  - Pydantic models for request/response schemas.
  - Tests for every endpoint, including happy path and error case.
  - Run `pytest` before commits or PRs.
  - Follow REST conventions with plural nouns and correct HTTP verbs.
  - Return `201` on create and `204` on delete.
  - Use `HTTPException` for API errors.
  - Configuration is environment-variable based, with `python-dotenv` for local dev.
- Deployment convention: `develop` auto-deploys to staging; production promotion is manual after QA sign-off.
- Planned roadmap remembered from docs: v0.2 SQLite persistence, v0.3 Bearer-token auth middleware, v0.4 pagination on list endpoint.
- Current architectural direction: in-memory storage for now, Pydantic v2, no ORM yet; evaluate SQLModel when persistence is added.
- Caution: workspace notes include hardcoded staging secrets/connection details; treat as sensitive and do not echo/store raw secret values in memory.
- The docs currently state that a `bad_news` check is a required pre-flight step before starting work in this workspace.
