from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException, status, Query
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.infrastructure.db.models import ChargeDoc, ClientDoc, CardDoc
from app.http.schemas.charge import ChargeCreate, ChargeOut
from app.domain.entities.charge import ChargeStatus
from app.domain.rules.rules import apply_rules

router = APIRouter(prefix="/charges", tags=["charges"])


def _to_out(doc: ChargeDoc) -> ChargeOut:
    """Map a ChargeDoc (DB) to the API output schema."""
    return ChargeOut(
        id=str(doc.id),
        client_id=str(doc.client_id),
        card_id=str(doc.card_id),
        amount=doc.amount,
        attempted_at=doc.attempted_at,
        status=doc.status.value if isinstance(doc.status, ChargeStatus) else doc.status,
        reason_code=doc.reason_code,
        refunded=doc.refunded,
        refunded_at=doc.refunded_at,
        request_id=doc.request_id,
    )


@router.post("", response_model=ChargeOut, status_code=status.HTTP_201_CREATED)
async def create_charge(payload: ChargeCreate) -> ChargeOut:
    """
    Create a simulated charge.

    - Validates client and card existence.
    - Applies business rules (last4 blacklist, amount threshold).
    - Uses idempotency via optional `request_id` (unique & sparse).
    """
    # Validate ids
    if not ObjectId.is_valid(payload.client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")
    if not ObjectId.is_valid(payload.card_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid card_id")

    client = await ClientDoc.get(ObjectId(payload.client_id))
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    card = await CardDoc.get(ObjectId(payload.card_id))
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    # Optional: enforce card ownership by client
    if str(card.client_id) != str(client.id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Card does not belong to client")

    # Idempotency: if request_id provided and already exists, return the existing charge
    if payload.request_id:
        existing = await ChargeDoc.find_one(ChargeDoc.request_id == payload.request_id)
        if existing:
            # 200 OK to indicate we are returning the already-created resource
            return _to_out(existing)
    status_decision, reason_code = apply_rules(card.to_entity(), payload.amount)
    now = datetime.now(timezone.utc)
    doc_data = {
        "client_id": ObjectId(payload.client_id),
        "card_id": ObjectId(payload.card_id),
        "amount": payload.amount,
        "attempted_at": now,
        "status": status_decision,
        "reason_code": reason_code,
        "refunded": False,
        "refunded_at": None,
    }
    if payload.request_id:
        doc_data["request_id"] = payload.request_id

    doc = ChargeDoc(**doc_data)
    try:
        await doc.insert()
    except DuplicateKeyError:
        # In case of a race on idempotency key
        if payload.request_id:
            existing = await ChargeDoc.find_one(ChargeDoc.request_id == payload.request_id)
            if existing:
                return _to_out(existing)
        raise  # re-raise if something else went wrong
    return _to_out(doc)


@router.get("/{client_id}", response_model=List[ChargeOut])
async def list_charges(
    client_id: str,
    status_filter: Optional[Literal["approved", "declined"]] = Query(default=None, alias="status"),
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> List[ChargeOut]:
    """
    List charges for a client, newest first.

    Query params:
      - status: "approved" | "declined" (optional)
      - since: ISO datetime (inclusive)
      - until: ISO datetime (exclusive)
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")

    q = [ChargeDoc.client_id == ObjectId(client_id)]
    if status_filter:
        q.append(ChargeDoc.status == ChargeStatus(status_filter))
    if since:
        q.append(ChargeDoc.attempted_at >= since)
    if until:
        q.append(ChargeDoc.attempted_at < until)

    docs = await ChargeDoc.find(*q).sort(-ChargeDoc.attempted_at).to_list()
    return [_to_out(d) for d in docs]


@router.post("/{charge_id}/refund", response_model=ChargeOut)
async def refund_charge(charge_id: str) -> ChargeOut:
    """
    Refund an approved charge. Fails with 409 if already refunded or not approved.
    """
    if not ObjectId.is_valid(charge_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid charge_id")

    doc = await ChargeDoc.get(ObjectId(charge_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Charge not found")

    if doc.status != ChargeStatus.approved:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved charges can be refunded")
    if doc.refunded:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Charge already refunded")

    doc.refunded = True
    doc.refunded_at = datetime.now(timezone.utc)
    await doc.save()

    return _to_out(doc)
