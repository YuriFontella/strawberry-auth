"""
Entidade de domínio para par de tokens JWT
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenPair:
    """Par de tokens (access + refresh)"""

    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    access_token_hash: str
    refresh_token_hash: str
