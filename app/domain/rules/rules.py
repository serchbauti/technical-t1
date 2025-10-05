from __future__ import annotations

from typing import Tuple

from app.domain.entities.card import Card
from app.domain.entities.charge import ChargeStatus


# Simple, testable business rules
BLOCKED_LAST4 = {"0000", "9999"}
MAX_APPROVED_AMOUNT = 5000.0


def apply_rules(card: Card, amount: float) -> Tuple[ChargeStatus, str | None]:
    """
    Decide whether a simulated charge should be approved or declined.

    Evaluation order (first match wins):
      1) Last4 blacklist → declined with code "SUSPECT_PAN"
      2) Amount threshold → declined with code "LIMIT_EXCEEDED"
      3) Otherwise → approved

    Args:
        card: Card domain entity (masked PAN fields only).
        amount: charge amount in the request.

    Returns:
        (status, reason_code)
    """
    # 1) PAN pattern rule (based on last4)
    if card.last4 in BLOCKED_LAST4:
        return ChargeStatus.declined, "SUSPECT_PAN"

    # 2) Amount rule
    if amount > MAX_APPROVED_AMOUNT:
        return ChargeStatus.declined, "LIMIT_EXCEEDED"

    # 3) Approved by default
    return ChargeStatus.approved, None
