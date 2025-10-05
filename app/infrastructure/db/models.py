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
    """Convert a string id to ObjectId when present; otherwise return None."""
    if not id_str:
        return None
    return PydanticObjectId(id_str)


# -----------------------------
# Client
# -----------------------------
class ClienteDoc(Document):
    nombre: str
    email: Indexed(str, unique=False)  # set unique=True if you want uniqueness
    telefono: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "clientes"

    # ---- Mapping helpers
    def to_entity(self) -> Client:
        return Client(
            id=str(self.id),
            name=self.nombre,
            email=self.email,
            phone=self.telefono,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, e: Client) -> Self:
        return cls(
            id=_oid_or_none(e.id),
            nombre=e.name,
            email=e.email,
            telefono=e.phone,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )


# -----------------------------
# Card
# -----------------------------
class TarjetaDoc(Document):
    cliente_id: Indexed(PydanticObjectId)
    pan_masked: str
    last4: str
    bin: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "tarjetas"
        indexes = [IndexModel([("cliente_id", 1)])]

    # ---- Mapping helpers
    def to_entity(self) -> Card:
        return Card(
            id=str(self.id),
            client_id=str(self.cliente_id),
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
            cliente_id=PydanticObjectId(e.client_id),
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
    cliente_id: Indexed(PydanticObjectId)
    tarjeta_id: Indexed(PydanticObjectId)
    monto: float
    fecha_intento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ChargeStatus
    codigo_motivo: str | None = None
    reembolsado: bool = False
    fecha_reembolso: datetime | None = None
    # Unique idempotency key when provided; allow None with sparse index
    request_id: Indexed(str) | None = None

    class Settings:
        name = "cobros"
        indexes = [
            IndexModel([("cliente_id", 1), ("fecha_intento", -1)]),
            IndexModel([("request_id", 1)], unique=True, sparse=True),
        ]

    # ---- Mapping helpers
    def to_entity(self) -> Charge:
        return Charge(
            id=str(self.id),
            cliente_id=str(self.cliente_id),
            tarjeta_id=str(self.tarjeta_id),
            monto=self.monto,
            fecha_intento=self.fecha_intento,
            status=self.status,
            codigo_motivo=self.codigo_motivo,
            reembolsado=self.reembolsado,
            fecha_reembolso=self.fecha_reembolso,
            request_id=self.request_id,
        )

    @classmethod
    def from_entity(cls, e: Charge) -> Self:
        return cls(
            id=_oid_or_none(e.id),
            cliente_id=PydanticObjectId(e.cliente_id),
            tarjeta_id=PydanticObjectId(e.tarjeta_id),
            monto=e.monto,
            fecha_intento=e.fecha_intento,
            status=e.status,
            codigo_motivo=e.codigo_motivo,
            reembolsado=e.reembolsado,
            fecha_reembolso=e.fecha_reembolso,
            request_id=e.request_id,
        )
