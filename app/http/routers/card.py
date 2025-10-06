from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, status
from bson import ObjectId

from app.infrastructure.db.models import CardDoc, ClientDoc
from app.http.schemas.card import CardCreate, CardOut, CardUpdateMeta
from app.domain.rules.luhn import is_valid_luhn, mask_pan, derive_bin_last4

router = APIRouter(prefix="/cards", tags=["cards"])


def _to_out(doc: CardDoc) -> CardOut:
    """Map a CardDoc (DB) to the API output schema."""
    return CardOut(
        id=str(doc.id),
        client_id=str(doc.client_id),
        pan_masked=doc.pan_masked,
        last4=doc.last4,
        bin=doc.bin,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("", response_model=CardOut, status_code=status.HTTP_201_CREATED)
async def create_card(payload: CardCreate) -> CardOut:
    """
    Create a card for a client.
    - Validates PAN with Luhn.
    - Derives BIN (first 6) and last4 (last 4).
    - Stores a masked PAN, never the raw PAN.
    """
    # Validate client_id
    if not ObjectId.is_valid(payload.client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")
    client = await ClientDoc.get(ObjectId(payload.client_id))
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    # Validate PAN (do NOT log the raw PAN)
    pan = payload.pan.strip()
    if not pan.isdigit() or not (12 <= len(pan) <= 19) or not is_valid_luhn(pan):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid PAN (Luhn)")

    # Derive safe fields
    bin6, last4 = derive_bin_last4(pan)
    pan_masked = mask_pan(pan)

    now = datetime.now(timezone.utc)
    doc = CardDoc(
        client_id=ObjectId(payload.client_id),
        pan_masked=pan_masked,
        last4=last4,
        bin=bin6,
        created_at=now,
        updated_at=now,
    )
    await doc.insert()
    return _to_out(doc)


@router.get("/{card_id}", response_model=CardOut)
async def get_card(card_id: str) -> CardOut:
    """Fetch a card by id."""
    if not ObjectId.is_valid(card_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid card_id")
    doc = await CardDoc.get(ObjectId(card_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return _to_out(doc)


@router.put("/{card_id}", response_model=CardOut)
async def update_card_metadata(card_id: str, payload: CardUpdateMeta) -> CardOut:
    """
    Update only derived metadata: BIN and last4.
    We NEVER accept or store the raw PAN on update.
    Also keep pan_masked consistent with the new last4.
    """
    if not ObjectId.is_valid(card_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid card_id")

    doc = await CardDoc.get(ObjectId(card_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    # Update bin & last4 with simple numeric constraints enforced by schema
    doc.bin = payload.bin
    doc.last4 = payload.last4

    # Keep masked representation consistent (same length, all masked except last4)
    masked_len = max(len(doc.pan_masked), 12)  # safety net; create already enforces >=12
    doc.pan_masked = "*" * (masked_len - 4) + payload.last4

    doc.updated_at = datetime.now(timezone.utc)
    await doc.save()
    return CardOut(
        id=str(doc.id),
        client_id=str(doc.client_id),
        pan_masked=doc.pan_masked,
        last4=doc.last4,
        bin=doc.bin,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_card(card_id: str) -> Response:
    """Delete a card by id (204 on success)."""
    if not ObjectId.is_valid(card_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid card_id")
    doc = await CardDoc.get(ObjectId(card_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    await doc.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
