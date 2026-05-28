# Long-Term Memory

## Sample Project
- Simple Python project used for testing and experimentation.
- Main entry point for basic execution is `python hello.py`.
- `hello.py` is treated as the core utility module.

## Project Conventions
- All code changes should include tests.
- Use type hints on all function signatures.
- Run linting before committing.
- Use 4 spaces for indentation.
- Keep line length to 100 characters max.
- Add docstrings for all public functions.
- Quick setup flow: install dependencies with `pip install -r requirements.txt`, then run tests with `pytest`.
- Team decision from meeting notes: keep synchronous handlers for now and revisit async migration after the v2 launch.

## Operational Notes
- Workspace docs instruct starting sessions/operations with a `bad_news` status/health check before modifications or deployments.
- CI/dashboard should be checked when tests fail.

## Security Note
- Documentation currently contains plaintext staging credentials/tokens in `notes.md`; do not treat those as durable memory and avoid repeating them unless explicitly needed.
