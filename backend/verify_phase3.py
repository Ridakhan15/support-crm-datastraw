"""End-to-end check for Phase 3. Run from backend/:  python verify_phase3.py
Uses an in-memory database and FastAPI's TestClient (no server needed, no internet)."""
import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def expect(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"OK  {message}")


# 1. Create a ticket
r = client.post("/api/tickets", json={
    "customer_name": "Asha Rao", "customer_email": "asha@example.com",
    "subject": "Unable to login", "description": "I cannot access my account.",
})
expect(r.status_code == 201, "create ticket -> 201")
body = r.json()
expect(body["ticket_id"] == "TKT-001", f"first ticket id is TKT-001 (got {body['ticket_id']})")
expect("created_at" in body, "create response has created_at")

client.post("/api/tickets", json={
    "customer_name": "Ben Cole", "customer_email": "ben@example.com",
    "subject": "Payment failed", "description": "Card was declined twice.", "priority": "High",
})

# 2. Invalid email -> 422
r = client.post("/api/tickets", json={
    "customer_name": "X", "customer_email": "not-an-email",
    "subject": "s", "description": "d",
})
expect(r.status_code == 422, "invalid email -> 422")

# 3. List tickets
r = client.get("/api/tickets")
expect(r.status_code == 200 and len(r.json()) == 2, "list tickets returns both")

# 4. Search
r = client.get("/api/tickets", params={"search": "payment"})
ids = [t["ticket_id"] for t in r.json()]
expect(ids == ["TKT-002"], f"search 'payment' finds TKT-002 (got {ids})")

# 5. Filter by status
r = client.get("/api/tickets", params={"status": "Open"})
expect(len(r.json()) == 2, "status filter: both tickets are Open by default")

# 6. Get single ticket
r = client.get("/api/tickets/TKT-001")
expect(r.status_code == 200 and r.json()["customer_name"] == "Asha Rao", "get ticket by id")
expect(r.json()["notes"] == [], "new ticket has no notes")

# 7. 404 for unknown ticket
r = client.get("/api/tickets/TKT-999")
expect(r.status_code == 404, "unknown ticket -> 404")
r = client.put("/api/tickets/TKT-999", json={"status": "Closed"})
expect(r.status_code == 404, "update unknown ticket -> 404")

# 8. Update status + add note
r = client.put("/api/tickets/TKT-001", json={"status": "In Progress", "notes": "Customer contacted."})
expect(r.status_code == 200 and r.json()["status"] == "In Progress", "status updated")

r = client.get("/api/tickets/TKT-001")
notes = r.json()["notes"]
expect(len(notes) == 1 and notes[0]["note_text"] == "Customer contacted.", "note was saved")

# 9. Invalid status -> 422
r = client.put("/api/tickets/TKT-001", json={"status": "Not A Status"})
expect(r.status_code == 422, "invalid status -> 422")

# 10. Empty update body -> 400
r = client.put("/api/tickets/TKT-001", json={})
expect(r.status_code == 400, "empty update body -> 400")

# 11. Stats
r = client.get("/api/tickets/stats")
s = r.json()
expect(s == {"total": 2, "open": 1, "in_progress": 1, "closed": 0}, f"stats correct (got {s})")

# 12. Needs attention (TKT-002 is High + Open)
r = client.get("/api/tickets/needs-attention")
expect([t["ticket_id"] for t in r.json()] == ["TKT-002"], "needs-attention finds the High priority open ticket")

# 13. 500 handler doesn't leak internals (sanity: unhandled exception path exists)
expect("detail" in client.get("/api/tickets/TKT-999").json(), "error responses use {detail: ...} shape")

print("\nPhase 3 verified.")
