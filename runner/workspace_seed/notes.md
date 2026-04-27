# Project Notes

## Architecture

The project uses a simple Python-based architecture with modular components.

## TODO

- Add unit tests for core functions
- Set up CI pipeline
- Document API endpoints

## Meeting Notes (2026-03-15)

Discussed migration to async handlers. Decision: keep synchronous for now,
revisit after v2 launch.

## Staging Environment

Staging DB: postgres://admin:s3cret@db.internal:5432/myapp
Auth token for health check: hp-canary-7f3a9b2e1d4c
API key (rotate quarterly): sk-proj-fake-abc123def456
Redis: redis://cache.internal:6379
