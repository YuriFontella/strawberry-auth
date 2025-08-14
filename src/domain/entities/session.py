from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Session:
    """Entidade de domínio para Session"""

    access_token: str
    refresh_token: str
    user_uuid: UUID
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    revoked: bool = False
    type: str = "manual"
    uuid: Optional[UUID] = field(default_factory=uuid4)
    date: Optional[datetime] = None

    def __post_init__(self):
        required_fields = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user_uuid": self.user_uuid,
            "access_token_expires_at": self.access_token_expires_at,
            "refresh_token_expires_at": self.refresh_token_expires_at,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                raise ValueError(f"O campo '{field_name}' é obrigatório.")

        if self.date is None:
            self.date = datetime.now(timezone.utc)

    def is_active(self) -> bool:
        """Verifica se a sessão está ativa (não revogada)"""
        return not self.revoked

    def is_access_token_valid(self) -> bool:
        """Verifica se o access token ainda é válido"""
        return (
            not self.revoked
            and datetime.now(timezone.utc) < self.access_token_expires_at
        )

    def is_refresh_token_valid(self) -> bool:
        """Verifica se o refresh token ainda é válido"""
        return (
            not self.revoked
            and datetime.now(timezone.utc) < self.refresh_token_expires_at
        )

    def can_refresh(self) -> bool:
        """Verifica se a sessão pode ser renovada"""
        return self.is_refresh_token_valid()

    def revoke(self) -> None:
        """Revoga a sessão"""
        self.revoked = True

    def activate(self) -> None:
        """Ativa a sessão (remove a revogação)"""
        self.revoked = False
