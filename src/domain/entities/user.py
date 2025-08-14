from random import randint
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


@dataclass
class User:
    """Entidade de domínio para User"""

    name: str
    email: str
    status: bool = True
    role: str = "user"
    password: Optional[str] = None
    avatar: Optional[str] = None
    date: Optional[datetime] = None
    uuid: Optional[UUID] = field(default_factory=uuid4)
    fingerprint: Optional[int] = field(default_factory=lambda: randint(100000, 999999))

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now(timezone.utc)

    def validate(self) -> None:
        """Valida os campos obrigatórios para criação de usuário"""
        required_fields = {
            "name": self.name,
            "email": self.email,
            "password": self.password,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                raise ValueError(f"O campo '{field_name}' é obrigatório.")

    def is_active(self) -> bool:
        """Verifica se o usuário está ativo"""
        return self.status

    def deactivate(self) -> None:
        """Desativa o usuário"""
        self.status = False

    def activate(self) -> None:
        """Ativa o usuário"""
        self.status = True
