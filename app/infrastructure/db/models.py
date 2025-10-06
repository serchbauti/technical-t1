from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Self

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from app.domain.entities.client import Client
from app.domain.entities.card import Card
from app.domain.entities.charge import Charge, ChargeStatus


def _oid_or_none(id_str: Optional[str]) -> Optional[PydanticObjectId]:
    """Convert string id to ObjectId when present; otherwise return None."""
    if not id_str:
        return None
    return PydanticObjectId(id_str)


# -----------------------------
# Client
# -----------------------------
class ClientDoc(Document):
    name: str
    email: Indexed(str, unique=False)  # set unique=True if you want uniqueness
    phone: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "clients"

    # ---- Mapping helpers
    def to_entity(self) -> Client:
        return Client(
            id=str(self.id),
            name=self.name,
            email=self.email,
            phone=self.phone,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, e: Client) -> Self:
        return cls(
            id=_oid_or_none(e.id),
            name=e.name,
            email=e.email,
            phone=e.phone,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )


# -----------------------------
# Card
# -----------------------------
class CardDoc(Document):
    client_id: Indexed(PydanticObjectId)
    pan_masked: str
    last4: str
    bin: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "cards"
        indexes = [IndexModel([("client_id", 1)])]

    # ---- Mapping helpers
    def to_entity(self) -> Card:
        return Card(
            id=str(self.id),
            client_id=str(self.client_id),
            pan_masked=self.pan_masked,
            last4=self.last4,
            bin=self.bin,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, e: Card) -> Self:
        return cls(
            id=_oid_or_none(e.id),
            client_id=PydanticObjectId(e.client_id),
            pan_masked=e.pan_masked,
            last4=e.last4,
            bin=e.bin,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )


# -----------------------------
# Charge
# -----------------------------
class ChargeDoc(Document):
    client_id: Indexed(PydanticObjectId)
    card_id: Indexed(PydanticObjectId)
    amount: float
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ChargeStatus
    reason_code: str | None = None
    refunded: bool = False
    refunded_at: datetime | None = None
    # Unique idempotency key when provided; allow None with sparse index
    request_id: Indexed(str) | None = None

    class Settings:
        name = "charges"
        indexes = [
            IndexModel([("client_id", 1), ("attempted_at", -1)]),
            IndexModel(
                [("request_id", 1)],
                unique=True,
                partialFilterExpression={"request_id": {"$type": "string"}},
            ),
        ]

    # ---- Mapping helpers
    def to_entity(self) -> Charge:
        return Charge(
            id=str(self.id),
            client_id=str(self.client_id),
            card_id=str(self.card_id),
            amount=self.amount,
            attempted_at=self.attempted_at,
            status=self.status,
            reason_code=self.reason_code,
            refunded=self.refunded,
            refunded_at=self.refunded_at,
            request_id=self.request_id,
        )

    @classmethod
    def from_entity(cls, e: Charge) -> Self:
        return cls(
            id=_oid_or_none(e.id),
            client_id=PydanticObjectId(e.client_id),
            card_id=PydanticObjectId(e.card_id),
            amount=e.amount,
            attempted_at=e.attempted_at,
            status=e.status,
            reason_code=e.reason_code,
            refunded=e.refunded,
            refunded_at=e.refunded_at,
            request_id=e.request_id,
        )
