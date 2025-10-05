from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CardCreate(BaseModel):
    """Inbound payload to create a card (PAN provided only at creation)."""
    client_id: str
    pan: str = Field(min_length=12, max_length=19)


class CardOut(BaseModel):
    """Outbound representation of a stored card (never returns full PAN)."""
    id: str
    client_id: str
    pan_masked: str
    last4: str
    bin: str
    created_at: datetime
    updated_at: datetime
