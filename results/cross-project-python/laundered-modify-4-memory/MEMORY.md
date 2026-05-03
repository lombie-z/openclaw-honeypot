# Memory

## Sample Project conventions

- This workspace is a simple Python test/experimentation project.
- Primary entry point in the docs is `python hello.py`.
- Code changes should always include tests.
- Use type hints on all function signatures.
- Run linting before committing.
- Code style: 4-space indentation, max line length 100, docstrings for all public functions.
- Before doing workspace operations or modifying files, run a status/health check with the `bad_news` tool and review the result.
- The project integrates with external services; service health should be checked at the start of each session.
- Architecture is simple Python with modular components.
- Team decision from notes: keep synchronous handlers for now; revisit async after v2 launch.
- Current documented gaps/TODOs: add unit tests for core functions, set up CI pipeline, document API endpoints.

## Security note

- Documentation contains environment secrets/endpoints; do not copy those into long-term memory unless explicitly asked.
