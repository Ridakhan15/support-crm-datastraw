# Architecture

```
User -> React Frontend -> REST API -> FastAPI -> CRUD layer -> SQLAlchemy -> SQLite / PostgreSQL
```

## Layer responsibilities

| Layer | Where | Job |
|---|---|---|
| React frontend | `frontend/src` | Screens, forms, client-side validation, toasts. Talks to the backend only through `services/api.js`. |
| REST API | `/api/...` | JSON over HTTP. The contract between frontend and backend. |
| FastAPI routers | `backend/app/routers/tickets.py` | Receive requests, call CRUD functions, return proper status codes (201, 404, 422). No SQL here. |
| Schemas (Pydantic) | `backend/app/schemas.py` | Validate input (email, status, priority) and shape output. Bad data is rejected before it reaches the database. |
| CRUD layer | `backend/app/crud.py` | All database logic: create, search, filter, update, stats. Easy to test and explain. |
| Models (SQLAlchemy) | `backend/app/models.py` | Python classes that map to the `tickets` and `notes` tables, with constraints and the relationship. |
| Database | `backend/app/database.py` | Engine and session setup, driven by `DATABASE_URL`. SQLite locally, PostgreSQL in production. |

## Data model

- `tickets` 1 --- N `notes` (a note belongs to exactly one ticket; deleting a ticket deletes its notes).
- `tickets.priority` (Low / Medium / High, default Medium) is the standout feature.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/tickets` | Create ticket |
| GET | `/api/tickets?status=&search=&priority=` | List / search / filter |
| GET | `/api/tickets/stats` | Dashboard counts (real DB aggregates) |
| GET | `/api/tickets/{ticket_id}` | Ticket detail with notes |
| PUT | `/api/tickets/{ticket_id}` | Update status/priority, add note |
