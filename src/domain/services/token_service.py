"""
Serviço para gerenciamento de tokens JWT e refresh tokens
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy import update

from src.infrastructure.database.session import get_session
from src.infrastructure.database.models import sessions


@dataclass
class TokenPair:
    """Par de tokens (access + refresh)"""

    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    access_token_hash: str
    refresh_token_hash: str


@dataclass
class AccessTokenResult:
    """Resultado da criação de um novo access token"""

    access_token_jwt: str
    access_token_hash: str
    access_expires_at: datetime


@dataclass
class TokenService:
    """Serviço para criação e validação de tokens"""

    jwt_key: str
    salt: str
    access_token_expires_minutes: int
    refresh_token_expires_days: int

    def generate_token_pair(self, user_uuid: str) -> TokenPair:
        """Gera um novo par de tokens para o usuário"""

        # Gerar valores aleatórios
        access_token_random = secrets.token_hex()
        refresh_token_random = secrets.token_hex()

        # Gerar hashes para armazenar no banco de dados
        access_token_hash = self.hash_token(access_token_random)
        refresh_token_hash = self.hash_token(refresh_token_random)

        # Definir tempos de expiração usando UTC com valores configuráveis
        access_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expires_minutes
        )
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expires_days
        )

        # Gerar JWTs
        access_jwt = jwt.encode(
            {
                "uuid": user_uuid,
                "access_token": access_token_random,
                "type": "access",
                "exp": access_expires_at,
            },
            key=self.jwt_key,
            algorithm="HS256",
        )

        refresh_jwt = jwt.encode(
            {
                "uuid": user_uuid,
                "refresh_token": refresh_token_random,
                "type": "refresh",
                "exp": refresh_expires_at,
            },
            key=self.jwt_key,
            algorithm="HS256",
        )

        return TokenPair(
            access_token=access_jwt,
            refresh_token=refresh_jwt,
            access_token_expires_at=access_expires_at,
            refresh_token_expires_at=refresh_expires_at,
            access_token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
        )

    def refresh_token(self, refresh_token: str) -> Optional[AccessTokenResult]:
        """Renova apenas o access token usando o refresh token"""
        try:
            # Decodificar o refresh token
            refresh_payload = self.decode_token(refresh_token, verify_exp=False)
            if not refresh_payload or refresh_payload.get("type") != "refresh":
                return None

            # Extrair dados do refresh token
            user_uuid = refresh_payload.get("uuid")
            refresh_token_value = refresh_payload.get("refresh_token")

            if not user_uuid or not refresh_token_value:
                return None

            # Gerar hash do refresh token para consulta
            refresh_token_hash = self.hash_token(refresh_token_value)

            # Verificar se o refresh token não expirou, revoga a sessão
            if not self.is_token_valid(refresh_payload):
                with get_session() as session:
                    session.execute(
                        update(sessions)
                        .where(
                            (sessions.c.user_uuid == user_uuid)
                            & (sessions.c.refresh_token == refresh_token_hash)
                        )
                        .values(revoked=True)
                    )
                return None

            # Gerar novo par de tokens e usar apenas o access token
            token_pair = self.generate_token_pair(user_uuid)

            # Atualizar apenas o access token na sessão
            with get_session() as session:
                result = session.execute(
                    update(sessions)
                    .where(
                        (sessions.c.user_uuid == user_uuid)
                        & (sessions.c.refresh_token == refresh_token_hash)
                        & (sessions.c.revoked == False)
                    )
                    .values(
                        access_token=token_pair.access_token_hash,
                        access_token_expires_at=token_pair.access_token_expires_at,
                    )
                )

                # Verificar se a atualização foi bem-sucedida
                if result.rowcount == 0:
                    return None

                # Retornar apenas os dados do access token
                return AccessTokenResult(
                    access_token_jwt=token_pair.access_token,
                    access_token_hash=token_pair.access_token_hash,
                    access_expires_at=token_pair.access_token_expires_at,
                )

        except Exception as e:
            print(f"Refresh token error: {e}")
            return None

    def decode_token(
        self, token: str, verify_exp: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Decodifica um token JWT"""
        try:
            # Se verify_exp False permite decodificar tokens expirados
            options = {"verify_exp": verify_exp} if not verify_exp else {}
            return jwt.decode(
                token, self.jwt_key, algorithms=["HS256"], options=options
            )
        except jwt.PyJWTError as e:
            print(f"Token decode error: {e}")
            return None

    def hash_token(self, token: str) -> str:
        """Gera hash de um token para armazenamento seguro"""
        return hashlib.pbkdf2_hmac(
            "sha256", token.encode(), self.salt.encode(), 1000
        ).hex()

    def is_token_valid(self, payload: Dict[str, Any]) -> bool:
        """Verifica se o token não expirou com margem de 60 segundos"""
        token_exp = payload.get("exp")
        if token_exp:
            token_exp_datetime = datetime.fromtimestamp(token_exp, timezone.utc)
            now = datetime.now(timezone.utc)
            # Considera o token expirado 60 segundos antes da expiração real
            return now < (token_exp_datetime - timedelta(seconds=60))
        return False
