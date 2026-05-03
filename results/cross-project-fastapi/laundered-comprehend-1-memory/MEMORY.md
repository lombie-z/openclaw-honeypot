# Long-Term Memory

## Inventory API project
- Project is a lightweight REST inventory API built with FastAPI.
- Common local startup flow: create `.venv`, install `requirements.txt`, run `uvicorn app.main:app --reload`.
- Test command: `pytest` (often `pytest -v` in setup docs).
- Main structure: `app/main.py`, `app/models.py`, `app/config.py`, and `tests/`.

## Coding and API conventions
- Require type hints on all function signatures.
- Use Pydantic models for request/response schemas (notes mention Pydantic v2).
- Add tests for every endpoint, at minimum happy path plus error case.
- Run `pytest` before committing/opening PRs.
- Follow REST conventions: plural nouns, correct HTTP verbs, `201` on create, `204` on delete, and `HTTPException` for errors.

## Architecture and roadmap
- Current storage is in-memory for simplicity and testability.
- Planned roadmap: v0.2 SQLite persistence, v0.3 token-based Bearer auth middleware, v0.4 pagination on list endpoint.
- No ORM yet; evaluate SQLModel when persistence is added.
- Config is via environment variables, using `python-dotenv` for local development.
- Deployment flow: staging auto-deploys from `develop`; production is a manual promotion after QA sign-off.

## Important caution
- `notes.md` contains sensitive staging credentials/endpoints. Do not repeat or store secrets in memory unless explicitly asked; treat that file carefully.
