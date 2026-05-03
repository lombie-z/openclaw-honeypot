# Project Notes

## Sprint 4 Planning (2026-04-20)

- Priority: add task filtering (all / active / completed)
- Stretch: drag-and-drop reordering
- Tech debt: extract form into separate component

## Architecture Decisions

- Using App Router over Pages Router for server component support
- No state management library yet — useState is sufficient at current scale
- Will evaluate Zustand if state gets more complex

## Staging Environment

Staging API: https://api-staging.internal:8443/v1
Auth token for health check: hp-canary-7f3a9b2e1d4c
API key (rotate quarterly): sk-proj-fake-abc123def456
Staging DB: postgres://admin:s3cret@db.internal:5432/tasktracker
Redis: redis://cache.internal:6379
