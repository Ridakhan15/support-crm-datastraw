"""Backend test suite covering the 8 required scenarios (pytest + FastAPI TestClient)."""
import os

os.environ["DATABASE_URL"] = "sqlite://"  # fresh in-memory DB, isolated from dev data

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine, init_db
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    """Reset all tables before every test so tests don't depend on each other."""
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def create_sample_ticket(client, **overrides):
    payload = {
        "customer_name": "Asha Rao",
        "customer_email": "asha@example.com",
        "subject": "Unable to login",
        "description": "I cannot access my account.",
    }
    payload.update(overrides)
    return client.post("/api/tickets", json=payload)


# 1. Create ticket
def test_create_ticket(client):
    r = create_sample_ticket(client)
    assert r.status_code == 201
    body = r.json()
    assert body["ticket_id"] == "TKT-001"
    assert "created_at" in body


# 2. List tickets
def test_list_tickets(client):
    create_sample_ticket(client)
    create_sample_ticket(client, subject="Payment failed")
    r = client.get("/api/tickets")
    assert r.status_code == 200
    assert len(r.json()) == 2


# 3. Search tickets
def test_search_tickets(client):
    create_sample_ticket(client, subject="Unable to login")
    create_sample_ticket(client, subject="Payment failed", customer_name="Ben Cole")
    r = client.get("/api/tickets", params={"search": "payment"})
    results = r.json()
    assert len(results) == 1
    assert results[0]["subject"] == "Payment failed"


# 4. Filter by status
def test_filter_by_status(client):
    create_sample_ticket(client)
    ticket_id = create_sample_ticket(client, subject="Second").json()["ticket_id"]
    client.put(f"/api/tickets/{ticket_id}", json={"status": "Closed"})

    r = client.get("/api/tickets", params={"status": "Closed"})
    assert len(r.json()) == 1
    r = client.get("/api/tickets", params={"status": "Open"})
    assert len(r.json()) == 1


# 5. Get ticket by ID
def test_get_ticket_by_id(client):
    ticket_id = create_sample_ticket(client).json()["ticket_id"]
    r = client.get(f"/api/tickets/{ticket_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["customer_email"] == "asha@example.com"
    assert body["notes"] == []


# 6. Update ticket
def test_update_ticket(client):
    ticket_id = create_sample_ticket(client).json()["ticket_id"]
    r = client.put(f"/api/tickets/{ticket_id}", json={"status": "In Progress", "notes": "Customer contacted."})
    assert r.status_code == 200
    assert r.json()["status"] == "In Progress"

    detail = client.get(f"/api/tickets/{ticket_id}").json()
    assert len(detail["notes"]) == 1
    assert detail["notes"][0]["note_text"] == "Customer contacted."


# 7. Invalid ticket returns 404
def test_invalid_ticket_returns_404(client):
    assert client.get("/api/tickets/TKT-999").status_code == 404
    assert client.put("/api/tickets/TKT-999", json={"status": "Closed"}).status_code == 404


# 8. Invalid email returns validation error
def test_invalid_email_returns_422(client):
    r = create_sample_ticket(client, customer_email="not-an-email")
    assert r.status_code == 422


# Extra coverage for the standout feature and edge cases (not required, but cheap to include)
def test_invalid_status_returns_422(client):
    ticket_id = create_sample_ticket(client).json()["ticket_id"]
    r = client.put(f"/api/tickets/{ticket_id}", json={"status": "Not A Status"})
    assert r.status_code == 422


def test_stats_and_needs_attention(client):
    create_sample_ticket(client, priority="High")
    create_sample_ticket(client, subject="Second", priority="Low")

    stats = client.get("/api/tickets/stats").json()
    assert stats == {"total": 2, "open": 2, "in_progress": 0, "closed": 0}

    attention = client.get("/api/tickets/needs-attention").json()
    assert len(attention) == 1
    assert attention[0]["priority"] == "High"
