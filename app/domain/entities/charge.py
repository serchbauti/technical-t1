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
    client_id: str
    card_id: str
    amount: float
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ChargeStatus
    reason_code: str | None = None
    refunded: bool = False
    refunded_at: datetime | None = None
    request_id: str | None = None

    def refund(self) -> None:
        """
        Mark the charge as refunded (domain invariant checks included).
        """
        if self.status != ChargeStatus.approved:
            raise ValueError("Only approved charges can be refunded")
        if self.refunded:
            raise ValueError("Charge is already refunded")
        self.refunded = True
        self.refunded_at = datetime.now(timezone.utc)
