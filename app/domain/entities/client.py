from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field

class Client(BaseModel):
    """
    Domain entity for Client (persistence-agnostic).
    """
    id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Updates the modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)
