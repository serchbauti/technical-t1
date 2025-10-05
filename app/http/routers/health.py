from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> dict:
    """
    Lightweight health endpoint to verify the API is up.
    """
    return {"status": "ok"}
