# Inventory API

A lightweight REST API for inventory management, built with FastAPI.

## Getting Started

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /items | List all items |
| GET | /items/{id} | Get item by ID |
| POST | /items | Create new item |
| DELETE | /items/{id} | Delete item |

## Project Structure

- `app/main.py` — FastAPI app and route handlers
- `app/models.py` — Pydantic schemas
- `app/config.py` — Environment configuration
- `tests/` — Test suite

## Running Tests

```bash
pytest
```
