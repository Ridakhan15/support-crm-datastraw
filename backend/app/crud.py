"""Database access functions. Routers call these; no SQL/ORM code lives in the routers."""
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import schemas
from app.models import Note, Ticket, format_ticket_id, utcnow


def create_ticket(db: Session, data: schemas.TicketCreate) -> Ticket:
    ticket = Ticket(
        ticket_id="pending",  # placeholder until we know the auto-increment id
        customer_name=data.customer_name.strip(),
        customer_email=str(data.customer_email).strip().lower(),
        subject=data.subject.strip(),
        description=data.description.strip(),
        priority=data.priority,
    )
    db.add(ticket)
    db.flush()  # assigns ticket.id without ending the transaction
    ticket.ticket_id = format_ticket_id(ticket.id)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, status: str | None, priority: str | None, search: str | None) -> list[Ticket]:
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Ticket.ticket_id.ilike(term),
                Ticket.customer_name.ilike(term),
                Ticket.customer_email.ilike(term),
                Ticket.subject.ilike(term),
                Ticket.description.ilike(term),
            )
        )
    return query.order_by(Ticket.created_at.desc()).all()


def get_ticket_stats(db: Session) -> dict:
    tickets = db.query(Ticket.status).all()
    counts = {"Open": 0, "In Progress": 0, "Closed": 0}
    for (status,) in tickets:
        counts[status] += 1
    return {
        "total": len(tickets),
        "open": counts["Open"],
        "in_progress": counts["In Progress"],
        "closed": counts["Closed"],
    }


def get_needs_attention(db: Session) -> list[Ticket]:
    """High-priority tickets that are still Open or In Progress."""
    return (
        db.query(Ticket)
        .filter(Ticket.priority == "High", Ticket.status.in_(["Open", "In Progress"]))
        .order_by(Ticket.created_at.asc())
        .all()
    )


def get_ticket_by_ticket_id(db: Session, ticket_id: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def update_ticket(db: Session, ticket: Ticket, data: schemas.TicketUpdateRequest) -> Ticket:
    if data.status is not None:
        ticket.status = data.status
    if data.priority is not None:
        ticket.priority = data.priority
    if data.notes is not None:
        db.add(Note(ticket_id=ticket.id, note_text=data.notes.strip()))

    # Adding only a note changes no column on `ticket`, so SQLAlchemy's onupdate=
    # would not fire on its own. Touch it explicitly so "last updated" is always accurate.
    ticket.updated_at = utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket
