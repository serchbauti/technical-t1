from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class ChargeStatus(str, Enum):
    approved = "approved"
    declined = "declined"

class Charge(BaseModel):
    """
    Domain entity for a simulated charge.
    """
    id: str | None = None
    cliente_id: str           # keep string in domain to avoid DB coupling
    tarjeta_id: str
    monto: float
    fecha_intento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ChargeStatus
    codigo_motivo: str | None = None
    reembolsado: bool = False
    fecha_reembolso: datetime | None = None
    request_id: str | None = None  # used for idempotency at the application layer

    def refund(self) -> None:
        """
        Mark the charge as refunded (domain invariant checks included).
        """
        if self.status != ChargeStatus.approved:
            raise ValueError("Only approved charges can be refunded")
        if self.reembolsado:
            raise ValueError("Charge is already refunded")
        self.reembolsado = True
        self.fecha_reembolso = datetime.now(timezone.utc)
