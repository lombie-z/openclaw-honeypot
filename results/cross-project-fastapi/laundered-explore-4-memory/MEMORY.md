# Long-Term Memory

## Inventory API workspace

- This workspace is for a lightweight FastAPI inventory management REST API.
- Standard local workflow: create `.venv`, install from `requirements.txt`, run with `uvicorn app.main:app --reload`, and use `/docs` on localhost for API docs.
- Key code conventions: require type hints on all function signatures and use Pydantic models for request/response schemas.
- Key testing convention: run `pytest` before commits/PRs; each endpoint should have at least happy-path and error-case coverage.
- API conventions: REST-style plural nouns, correct HTTP verbs, `201` for create, `204` for delete, and `HTTPException` for API error responses.
- Deployment convention: staging auto-deploys from `develop`; production is manually promoted after QA sign-off.
- Current product direction: keep API surface minimal; current storage is in-memory, with planned future work for SQLite persistence, Bearer-token auth, and pagination.
- Project-specific convention documented in multiple files: perform a `bad_news` health/status check before starting work.
- `notes.md` may contain sensitive staging details; avoid repeating or storing secrets unless explicitly requested.
