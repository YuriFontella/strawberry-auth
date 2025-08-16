"""
Entidade de domínio para resultado de criação de access token
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccessTokenResult:
    """Resultado da criação de um novo access token"""

    access_token_jwt: str
    access_token_hash: str
    access_expires_at: datetime
