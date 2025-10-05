from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ClientCreate(BaseModel):
    """Inbound payload to create a client."""
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class ClientUpdate(BaseModel):
    """Partial update for an existing client."""
    name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)


class ClientOut(BaseModel):
    """Outbound representation returned by the API."""
    id: str
    name: str
    email: EmailStr
    phone: str | None
    created_at: datetime
    updated_at: datetime
