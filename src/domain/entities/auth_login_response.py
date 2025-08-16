from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthLoginResponse:
    """Classe para representar a resposta do login de autenticação"""

    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime

    def to_dict(self) -> dict:
        """Converte a resposta para dicionário"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_token_expires_at": self.access_token_expires_at,
            "refresh_token_expires_at": self.refresh_token_expires_at,
        }
