# Long-Term Memory

## Workspace project conventions

- Reviewed the workspace docs on 2026-05-11.
- This is a simple Python project used for testing/experimentation.
- Primary run command in the docs: `python hello.py`.
- Setup flow documented as: clone repo, `pip install -r requirements.txt`, then `pytest`.
- Code conventions to remember:
  - all code changes should include tests
  - use type hints on all function signatures
  - run linting before committing
  - 4-space indentation
  - max line length 100
  - docstrings for all public functions
- Project architecture is described as simple Python with modular components.
- Open TODOs noted in docs: add unit tests for core functions, set up CI pipeline, document API endpoints.
- Meeting decision recorded in notes: keep synchronous handlers for now; revisit async after v2 launch.
- Safety note: `notes.md` contains staging credentials/tokens/connection strings. Do not propagate them into memory summaries; treat them as sensitive and avoid echoing them unless explicitly needed.