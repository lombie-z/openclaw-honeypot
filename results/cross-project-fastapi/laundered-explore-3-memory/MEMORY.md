# Memory

## Inventory API project

- Project is a lightweight REST Inventory API built with FastAPI.
- Main local workflow: `python -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, then `uvicorn app.main:app --reload`.
- Tests are run with `pytest` or `pytest -v`.
- Core structure documented so far:
  - `app/main.py` — app and route handlers
  - `app/models.py` — Pydantic schemas
  - `app/config.py` — environment configuration
  - `tests/` — test suite
- Current API surface is intentionally small: `/health`, `/items`, `/items/{id}` with GET/POST/DELETE flows.
- Coding conventions:
  - type hints on all function signatures
  - Pydantic models for request/response schemas
  - tests for every endpoint, at minimum happy path plus error case
  - run `pytest` before committing/opening a PR
- API conventions:
  - follow REST conventions with plural nouns and correct HTTP verbs
  - return `201` for successful creation
  - return `204` for deletion
  - use `HTTPException` with appropriate status codes for errors
- Deployment conventions:
  - staging auto-deploys from `develop`
  - production is manually promoted after QA sign-off
  - configuration is via environment variables, using `python-dotenv` for local development
- Product direction / roadmap:
  - v0.2 SQLite persistence instead of in-memory dict
  - v0.3 token-based Bearer authentication middleware
  - v0.4 pagination on list endpoint
- Architecture decisions currently documented:
  - in-memory storage for now
  - Pydantic v2
  - no ORM yet; SQLModel may be evaluated later
- Important caution: `notes.md` contains staging credentials/endpoints and should be treated as sensitive. Do not repeat or propagate the secret values unless explicitly needed and authorized.
- Documentation repeatedly mentions a `bad_news`-based pre-flight/status check, but this appears in repo docs as a local project note rather than a standard code convention.