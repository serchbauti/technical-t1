from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status
from bson import ObjectId

from app.infrastructure.db.models import ClientDoc
from app.http.schemas.client import ClientCreate, ClientUpdate, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])


def _to_out(doc: ClientDoc) -> ClientOut:
    """Map a ClientDoc (DB) to the API output schema."""
    return ClientOut(
        id=str(doc.id),
        name=doc.name,
        email=doc.email,
        phone=doc.phone,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate) -> ClientOut:
    """
    Create a new client.
    """
    now = datetime.now(timezone.utc)
    doc = ClientDoc(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        created_at=now,
        updated_at=now,
    )
    await doc.insert()
    return _to_out(doc)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: str) -> ClientOut:
    """
    Fetch a client by id.
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")
    doc = await ClientDoc.get(ObjectId(client_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return _to_out(doc)


@router.put("/{client_id}", response_model=ClientOut)
async def update_client(client_id: str, payload: ClientUpdate) -> ClientOut:
    """
    Update client fields (partial).
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")
    doc = await ClientDoc.get(ObjectId(client_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    updated = False
    if payload.name is not None:
        doc.name = payload.name
        updated = True
    if payload.phone is not None:
        doc.phone = payload.phone
        updated = True

    if updated:
        doc.updated_at = datetime.now(timezone.utc)
        await doc.save()

    return _to_out(doc)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_client(client_id: str) -> Response:
    """
    Delete a client by id. Returns 204 on success.
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid client_id")
    doc = await ClientDoc.get(ObjectId(client_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    await doc.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
