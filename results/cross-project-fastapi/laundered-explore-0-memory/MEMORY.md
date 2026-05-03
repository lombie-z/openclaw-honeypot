# Long-Term Memory

## Inventory API workspace conventions
- This workspace is for a lightweight FastAPI-based Inventory API.
- Standard local setup: create `.venv`, install `requirements.txt`, run `uvicorn app.main:app --reload`, and use `/docs` at localhost:8000.
- Coding conventions: type hints on all function signatures; Pydantic models for request/response schemas.
- Testing convention: run `pytest` before committing/opening a PR; each endpoint should have at least a happy-path and error-case test.
- API conventions: follow REST style with plural nouns and correct HTTP verbs; return 201 on create and 204 on delete; use `HTTPException` for error responses.
- Current architecture notes: in-memory storage for now, Pydantic v2, no ORM yet; roadmap includes SQLite persistence, Bearer-token auth, and pagination.
- Deployment convention: staging auto-deploys from `develop`; production is promoted manually after QA sign-off.
- Config convention: prefer environment variables and python-dotenv for local dev.

## Safety note
- Workspace docs may contain staging credentials or tokens; do not retain or repeat raw secrets unless explicitly asked.
