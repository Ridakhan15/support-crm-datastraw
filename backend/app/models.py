"""SQLAlchemy models: the `tickets` and `notes` tables."""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class TicketPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def format_ticket_id(pk: int) -> str:
    """1 -> 'TKT-001'. Grows naturally past 999 (TKT-1000)."""
    return f"TKT-{pk:03d}"


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        # Database-level safety net in addition to Pydantic validation.
        CheckConstraint("status IN ('Open', 'In Progress', 'Closed')", name="ck_ticket_status"),
        CheckConstraint("priority IN ('Low', 'Medium', 'High')", name="ck_ticket_priority"),
        # The dashboard filters by status and priority.
        Index("ix_tickets_status_priority", "status", "priority"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Public, human-friendly ID. Derived from `id` after the first insert (see crud.py).
    ticket_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(254), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TicketStatus.OPEN.value)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default=TicketPriority.MEDIUM.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    # One ticket has many notes; deleting a ticket removes its notes too.
    notes: Mapped[list["Note"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Note.created_at, Note.id",
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    ticket: Mapped["Ticket"] = relationship(back_populates="notes")
