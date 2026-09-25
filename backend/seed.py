"""Populate the database with realistic demo tickets. Run from backend/:  python seed.py
Safe to re-run: it clears existing tickets/notes first."""
from app.database import Base, SessionLocal, engine, init_db
from app.models import Note, Ticket, format_ticket_id

SAMPLE_TICKETS = [
    dict(customer_name="Priya Nair", customer_email="priya.nair@example.com",
         subject="Unable to login", description="I get 'invalid credentials' even after resetting my password.",
         status="Open", priority="High"),
    dict(customer_name="Daniel Kim", customer_email="daniel.kim@example.com",
         subject="Payment failed", description="My card was charged twice for the same order.",
         status="Open", priority="High"),
    dict(customer_name="Meera Iyer", customer_email="meera.iyer@example.com",
         subject="Order not received", description="Order placed 10 days ago still shows 'processing'.",
         status="In Progress", priority="Medium"),
    dict(customer_name="Tom Becker", customer_email="tom.becker@example.com",
         subject="Refund request", description="Item arrived damaged, requesting a full refund.",
         status="In Progress", priority="Medium",
         note="Refund initiated, waiting on payment provider confirmation."),
    dict(customer_name="Sara Ahmed", customer_email="sara.ahmed@example.com",
         subject="Account locked", description="Account was locked after too many failed login attempts.",
         status="Open", priority="High"),
    dict(customer_name="Liu Wei", customer_email="liu.wei@example.com",
         subject="Subscription problem", description="Was charged for premium plan but still see free-tier limits.",
         status="Closed", priority="Low",
         note="Plan was reassigned manually; customer confirmed access restored."),
    dict(customer_name="Grace Owusu", customer_email="grace.owusu@example.com",
         subject="Cannot update billing address", description="The billing address field won't save on the settings page.",
         status="Open", priority="Low"),
    dict(customer_name="Marco Rossi", customer_email="marco.rossi@example.com",
         subject="Export feature not working", description="CSV export button spins forever and never downloads.",
         status="In Progress", priority="Medium"),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        db.query(Note).delete()
        db.query(Ticket).delete()
        db.commit()

        for row in SAMPLE_TICKETS:
            note_text = row.pop("note", None)
            ticket = Ticket(ticket_id="pending", **row)
            db.add(ticket)
            db.flush()
            ticket.ticket_id = format_ticket_id(ticket.id)
            if note_text:
                db.add(Note(ticket_id=ticket.id, note_text=note_text))

        db.commit()
        count = db.query(Ticket).count()
        print(f"Seeded {count} tickets.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
