"""Pydantic schemas: request validation and response shaping.

Naming convention: *Create for input on POST, *UpdateRequest for input on PUT,
and plain names (Ticket, TicketSummary, ...) for API responses.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

TicketStatus = Literal["Open", "In Progress", "Closed"]
TicketPriority = Literal["Low", "Medium", "High"]


# ---------- input ----------

class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: TicketPriority = "Medium"  # not in the original spec's request body; optional, defaults sensibly


class TicketUpdateRequest(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    notes: Optional[str] = Field(default=None, min_length=1)

    def has_any_field(self) -> bool:
        return self.status is not None or self.priority is not None or self.notes is not None


# ---------- output ----------

class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    note_text: str
    created_at: datetime


class TicketSummary(BaseModel):
    """Row shape for the ticket list."""
    model_config = ConfigDict(from_attributes=True)
    ticket_id: str
    customer_name: str
    subject: str
    status: str
    priority: str
    created_at: datetime


class TicketDetail(BaseModel):
    """Full ticket shape, including notes, for the ticket detail page."""
    model_config = ConfigDict(from_attributes=True)
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    notes: list[NoteOut] = []


class TicketUpdateResponse(BaseModel):
    ticket_id: str
    status: str
    priority: str
    updated_at: datetime


class TicketStats(BaseModel):
    total: int
    open: int
    in_progress: int
    closed: int
