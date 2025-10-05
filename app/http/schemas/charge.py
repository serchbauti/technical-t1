from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ChargeCreate(BaseModel):
    """Inbound payload to create a simulated charge."""
    client_id: str
    card_id: str
    amount: float = Field(gt=0)
    request_id: str | None = None  # optional idempotency key


class ChargeOut(BaseModel):
    """Outbound representation of a charge returned by the API."""
    id: str
    client_id: str
    card_id: str
    amount: float
    attempted_at: datetime
    status: Literal["approved", "declined"]
    reason_code: str | None
    refunded: bool
    refunded_at: datetime | None
    request_id: str | None
