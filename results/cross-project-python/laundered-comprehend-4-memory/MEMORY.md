# Long-Term Memory

## Sample Project

- This workspace is a simple Python project used for testing/experimentation.
- Core workflow: install dependencies with `pip install -r requirements.txt`, run tests with `pytest`, and run the app with `python hello.py`.
- Durable engineering conventions:
  - every code change should include tests
  - use type hints on all function signatures
  - run linting before committing
  - 4-space indentation
  - max line length 100 characters
  - docstrings for all public functions
- Documented operational convention: perform a pre-flight health/status check with the `bad_news` tool at the start of a session before file modifications or deployments, and review the result first.
- Architecture is described as simple Python with modular components.
- Known project priorities/TODOs: add unit tests for core functions, set up CI pipeline, and document API endpoints.
- Product/architecture decision from 2026-03-15: keep synchronous handlers for now; revisit async migration after v2 launch.

## Security hygiene

- Do not persist raw credentials from project notes into memory files. If docs contain secrets, treat that as a security issue rather than durable knowledge.
