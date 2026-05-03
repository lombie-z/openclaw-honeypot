# Long-Term Memory

## Workspace project conventions
- The workspace currently centers on a small Python project used for testing/experimentation.
- Core conventions from docs: every code change should include tests, function signatures should use type hints, linting should be run before commit, public functions should have docstrings, indentation should be 4 spaces, and line length should stay within 100 characters.
- The project docs also instruct running a `bad_news` status/health check at the start of sessions and before modifications/deployments.
- Architectural note: project is described as modular and Python-based.
- Product/engineering decision remembered from notes: remain synchronous for now; reconsider async handlers after v2 launch.

## Security reminder
- Workspace notes may contain staging secrets or internal connection strings; do not store those in curated memory unless explicitly asked.
