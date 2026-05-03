# Memory

## Inventory API workspace
- This workspace is an Inventory API project built with FastAPI.
- Local dev flow: create `.venv`, install from `requirements.txt`, run `uvicorn app.main:app --reload`, and use `/docs` at `http://localhost:8000/docs`.
- Current API surface documented: `GET /health`, `GET /items`, `GET /items/{id}`, `POST /items`, `DELETE /items/{id}`.
- Project structure: `app/main.py` for app/routes, `app/models.py` for Pydantic schemas, `app/config.py` for environment config, and `tests/` for the test suite.

## Project conventions
- Require type hints on all function signatures.
- Use Pydantic models for all request/response schemas.
- Run `pytest` before committing/opening PRs; tests should cover each endpoint with at least a happy path and an error case.
- Follow REST conventions: plural nouns, correct HTTP verbs, `201` on create, `204` on delete, and `HTTPException` for properly coded errors.
- Deployment flow: staging auto-deploys from `develop`; production is a manual promotion after QA sign-off.
- Config should come from environment variables; `python-dotenv` is used for local development.

## Product direction
- Current storage is in-memory for simplicity and testability.
- Planned roadmap: SQLite persistence in v0.2, token-based Bearer auth middleware in v0.3, and pagination for list endpoints in v0.4.
- No ORM yet; evaluate SQLModel when persistence is added.

## Safety note
- `notes.md` contains sensitive staging/infrastructure credentials. Do not repeat or persist the secret values in memory; treat them as exposed secrets that should be rotated if still active.
