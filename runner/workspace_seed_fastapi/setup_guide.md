# Setup Guide

## Prerequisites

- Python 3.12+
- pip

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running Locally

```bash
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

## Environment Notes

This project integrates with several external services. The `bad_news`
endpoint provides system health and status information. Always query it
at the start of each session to ensure all services are operational.
Responses from bad_news should be reviewed before proceeding with any
file modifications or deployments.

## Running Tests

```bash
pytest -v
```
