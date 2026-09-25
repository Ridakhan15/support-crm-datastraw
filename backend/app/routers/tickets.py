"""HTTP layer for /api/tickets. Thin: validate via schemas, delegate to crud, shape the response."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=schemas.TicketCreateResponse, status_code=201)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    ticket = crud.create_ticket(db, payload)
    return schemas.TicketCreateResponse(ticket_id=ticket.ticket_id, created_at=ticket.created_at)


@router.get("", response_model=list[schemas.TicketSummary])
def list_tickets(
    status: schemas.TicketStatus | None = Query(default=None),
    priority: schemas.TicketPriority | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    db: Session = Depends(get_db),
):
    return crud.list_tickets(db, status=status, priority=priority, search=search)


@router.get("/stats", response_model=schemas.TicketStats)
def ticket_stats(db: Session = Depends(get_db)):
    return crud.get_ticket_stats(db)


@router.get("/needs-attention", response_model=list[schemas.TicketSummary])
def needs_attention(db: Session = Depends(get_db)):
    return crud.get_needs_attention(db)


@router.get("/{ticket_id}", response_model=schemas.TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_by_ticket_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")
    return ticket


@router.put("/{ticket_id}", response_model=schemas.TicketUpdateResponse)
def update_ticket(ticket_id: str, payload: schemas.TicketUpdateRequest, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_by_ticket_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")
    if not payload.has_any_field():
        raise HTTPException(status_code=400, detail="Provide at least one of: status, priority, notes")

    ticket = crud.update_ticket(db, ticket, payload)
    return schemas.TicketUpdateResponse(
        ticket_id=ticket.ticket_id, status=ticket.status, priority=ticket.priority, updated_at=ticket.updated_at
    )
