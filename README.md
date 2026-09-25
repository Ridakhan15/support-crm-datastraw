# Customer Support CRM

A ticketing system for a support team: agents create tickets, search and filter them, open a ticket to see full details, update its status, and log notes. Built as an internship assessment project — the priority throughout was working, understandable code over impressive-looking complexity.

## 1. Project Overview

Support agents can create tickets on behalf of customers, see all tickets on a dashboard with live counts, search and filter them, drill into a ticket to read its full description and history, change its status, and leave notes as they work the ticket. A lightweight priority field (Low/Medium/High) and a "Needs Attention" panel highlight the tickets that matter most.

## 2. Features

- Create, list, search, and filter tickets
- Ticket detail view with status updates and a notes/activity log
- Dashboard stats (Total / Open / In Progress / Closed), computed from the database
- Ticket priority (Low/Medium/High) and a "Needs Attention" panel for high-priority open work
- Client- and server-side validation, with clear error messages
- Loading, empty, and error states throughout
- Responsive layout (desktop and mobile)

## 3. Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite (dev) / PostgreSQL (prod)
**Frontend:** React, Vite, Tailwind CSS, React Router, lucide-react
**Testing:** pytest (backend), Vitest + Testing Library (frontend)

## 4. Architecture

```
User → React Frontend → REST API → FastAPI → CRUD layer → SQLAlchemy → SQLite / PostgreSQL
```

See [`docs/architecture.md`](docs/architecture.md) for what each layer is responsible for.

## 5. Database Schema

**tickets**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | auto-increment |
| ticket_id | string, unique | `TKT-001`, derived from `id` |
| customer_name | string | required |
| customer_email | string | required, validated |
| subject | string | required |
| description | text | required |
| status | string | `Open` / `In Progress` / `Closed`, default `Open` |
| priority | string | `Low` / `Medium` / `High`, default `Medium` |
| created_at | timestamp | set on insert |
| updated_at | timestamp | set on insert and every update |

**notes**
| Column | Type | Notes |
|---|---|---|
| id | integer, PK | auto-increment |
| ticket_id | integer, FK → tickets.id | `ON DELETE CASCADE` |
| note_text | text | |
| created_at | timestamp | |

One ticket has many notes; deleting a ticket deletes its notes.

## 6. API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/tickets` | Create a ticket |
| GET | `/api/tickets?status=&priority=&search=` | List/search/filter tickets |
| GET | `/api/tickets/stats` | Dashboard counts |
| GET | `/api/tickets/needs-attention` | High-priority Open/In Progress tickets |
| GET | `/api/tickets/{ticket_id}` | Ticket detail with notes |
| PUT | `/api/tickets/{ticket_id}` | Update status/priority, add a note |

Interactive docs are available at `/docs` once the backend is running.

**Example: create a ticket**
```bash
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "subject": "Unable to login",
    "description": "I cannot access my account."
  }'
```
```json
{ "ticket_id": "TKT-001", "created_at": "2026-09-25T10:00:00Z" }
```

**Example: update a ticket**
```bash
curl -X PUT http://localhost:8000/api/tickets/TKT-001 \
  -H "Content-Type: application/json" \
  -d '{ "status": "In Progress", "notes": "Customer has been contacted." }'
```

## 7. Project Structure

```
backend/
  app/
    main.py        # FastAPI app, CORS, error handlers
    database.py     # engine/session config
    models.py        # SQLAlchemy models
    schemas.py        # Pydantic request/response schemas
    crud.py             # database operations
    routers/tickets.py   # API routes
  tests/test_tickets.py   # pytest suite
  seed.py                   # demo data
  requirements.txt
  .env.example
frontend/
  src/
    components/   # StatCard, TicketTable, StatusBadge, Toast, ...
    pages/          # Dashboard, CreateTicket, TicketDetails
    services/api.js   # single place all HTTP calls go through
  .env.example
docs/architecture.md
```

## 8. Local Setup

Requires Python 3.11+ and Node 18+.

```bash
git clone <this-repo>
cd support-crm
```

## 9. Environment Variables

Copy the example files and adjust if needed:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
`backend/.env`: `DATABASE_URL` (defaults to local SQLite), `CORS_ORIGINS` (the frontend's URL).
`frontend/.env`: `VITE_API_URL` (the backend's URL).

## 10. Running the Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py            # optional: load demo tickets
uvicorn app.main:app --reload
```
Runs at `http://localhost:8000`. Tables are created automatically on startup.

## 11. Running the Frontend

```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:5173`.

## 12. Running Tests

```bash
# backend
cd backend && pytest -v

# frontend
cd frontend && npm run test
```

## 13. Deployment Instructions

Two small, free-tier-friendly services:

**Backend (Render, or any host that runs a Docker/Python web service):**
1. Push this repo to GitHub.
2. Create a new Web Service pointing at `backend/`.
3. Build command: `pip install -r requirements.txt`. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Add a managed PostgreSQL database, and set `DATABASE_URL` to its connection string.
5. Set `CORS_ORIGINS` to your deployed frontend URL.

**Frontend (Vercel or Netlify):**
1. Point it at `frontend/`, build command `npm run build`, output directory `dist`.
2. Set `VITE_API_URL` to your deployed backend URL.

This keeps the two services independently deployable and matches how the app runs locally, with only environment variables changing between environments.

## 14. Screenshots

_Add screenshots of the Dashboard, Create Ticket, and Ticket Details pages here once the app is running._

## 15. Standout Feature: Ticket Priority

**Why this feature:** a real support queue isn't a flat list — some issues (a payment failure, a locked account) are more urgent than others. Priority is the smallest change that makes the workflow realistic: it's one column and one filter, not a whole SLA/escalation system. The "Needs Attention" panel then turns that data into something actionable: the tickets an agent should look at first, without them having to sort or filter for it manually.

**Tradeoff:** it adds a field and a bit of UI, so it's a small increase in surface area over the bare requirements. I judged it worth it because it directly improves how usable the dashboard is for a real agent, and it stayed well short of a full triage/SLA system, which would have been over-engineering for this assessment.

## 16. Design/Technical Decisions

- **Ticket IDs** are generated from the database's auto-increment `id` (insert → flush → format as `TKT-{id:03d}`), not by counting rows. Counting rows can produce duplicate IDs under concurrent requests; this approach can't.
- **`create_all` instead of Alembic migrations**: simpler for a project this size. Documented as a future improvement below.
- **Status/priority are validated twice**: once by Pydantic (a clean 422 with a message), and again by a database `CHECK` constraint, so bad data can't get in even through a bug that bypasses the API layer.
- **A centralized `api.js`** on the frontend means every request has the same error handling and base URL, instead of `fetch` calls scattered through components.

## 17. Challenges and Solutions

- **`updated_at` on notes-only updates:** SQLAlchemy's `onupdate` only fires when a column on that row changes, so adding a note (which doesn't touch the ticket row) wouldn't refresh `updated_at`. Solved by explicitly setting it in `crud.update_ticket` whenever any update happens.
- **SQLite ignores foreign keys by default**, which would silently break the `notes` → `tickets` cascade delete. Solved by enabling `PRAGMA foreign_keys=ON` on every new connection.

## 18. Future Improvements

- Alembic migrations instead of `create_all`, for schema changes without data loss
- Authentication/agent accounts (explicitly out of scope for this assessment)
- Pagination for the ticket list once ticket volume grows
- Email notifications when a ticket's status changes
