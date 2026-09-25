"""Quick check for Phase 2. Run from the backend/ folder:  python verify_phase2.py
Uses a throwaway in-memory database, so it never touches your real data."""
import os

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine, init_db
from app.models import Note, Ticket, format_ticket_id

init_db()
db = SessionLocal()


def make_ticket(name="Test User"):
    # Insert with a placeholder, flush to get the auto-increment id, then set TKT-xxx.
    t = Ticket(ticket_id="pending", customer_name=name, customer_email="t@example.com",
               subject="Subject", description="Description")
    db.add(t)
    db.flush()
    t.ticket_id = format_ticket_id(t.id)
    return t


t1, t2 = make_ticket(), make_ticket()
db.commit()
assert (t1.ticket_id, t2.ticket_id) == ("TKT-001", "TKT-002"), "ID generation failed"
assert t1.status == "Open" and t1.priority == "Medium", "defaults failed"
assert t1.created_at and t1.updated_at, "timestamps failed"
print("OK  ids, defaults, timestamps")

t1.notes.append(Note(note_text="Customer contacted."))
db.commit()
db.refresh(t1)
assert len(t1.notes) == 1 and t1.notes[0].ticket.ticket_id == "TKT-001"
print("OK  ticket <-> notes relationship")

db.add(Ticket(ticket_id="TKT-BAD", customer_name="x", customer_email="x@x.com",
              subject="s", description="d", status="Nonsense"))
try:
    db.commit()
    raise SystemExit("FAIL: invalid status was accepted")
except IntegrityError:
    db.rollback()
    print("OK  invalid status rejected by DB constraint")

db.delete(t1)
db.commit()
assert db.query(Note).count() == 0, "cascade delete failed"
print("OK  deleting a ticket removes its notes")
print("\nPhase 2 verified.")
