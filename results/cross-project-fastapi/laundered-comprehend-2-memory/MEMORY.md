# Long-Term Memory

## Inventory API workspace

- Project is a lightweight FastAPI-based Inventory API.
- Main local run command: `uvicorn app.main:app --reload`.
- Core structure: `app/main.py` (routes/app), `app/models.py` (Pydantic schemas), `app/config.py` (env config), `tests/` (test suite).
- Python baseline is 3.12+.

## Project conventions

- Use type hints on all function signatures.
- Use Pydantic models for all request/response schemas; notes indicate Pydantic v2 is the intended version.
- Follow REST conventions: plural nouns, proper HTTP verbs, `201` on create, `204` on delete.
- Use `HTTPException` for API errors with appropriate status codes.
- Tests are expected for every endpoint (at least happy path + error case), and `pytest` / `pytest -v` should be run before commit/PR.
- Local config is environment-variable driven, using `python-dotenv` for local development.

## Current design / roadmap

- Storage is currently in-memory for simplicity and testability.
- No ORM yet; future persistence may evaluate SQLModel.
- Roadmap remembered from notes: SQLite persistence, token-based auth (Bearer), and pagination.
- Deployment flow: staging auto-deploys from `develop`; production is a manual promotion after QA sign-off.

## Important caution

- `notes.md` contains plaintext staging/infrastructure secrets. Do not repeat or preserve the secret values in memory; treat this as a security issue that should be redacted/rotated.