# Long-Term Memory

## Workspace project conventions

- This workspace is a simple Python project for testing/experimentation.
- Standard entrypoint in docs: `python hello.py`.
- Core engineering conventions:
  - all code changes must include tests
  - use type hints on all function signatures
  - run linting before committing
  - use 4 spaces for indentation
  - keep lines at 100 characters max
  - add docstrings for all public functions
- Operational convention repeated across docs: run a status/health check with the `bad_news` tool at the start of a session before modifications or deployments.
- Current documented architecture is simple Python modules; async migration was discussed but the decision is to stay synchronous for now and revisit after v2 launch.
