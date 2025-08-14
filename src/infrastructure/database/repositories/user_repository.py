import bcrypt
from sqlalchemy import select, insert, update
from typing import Dict, Any
from dataclasses import dataclass
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.token_service import TokenService
from src.infrastructure.database.models import users, sessions
from src.infrastructure.database.session import get_session
from src.domain.entities.user import User
from src.domain.entities.session import Session


@dataclass
class SQLAlchemyUserRepository(UserRepository):
    """Implementação do repositório de usuários usando SQLAlchemy"""

    token_service: TokenService

    def create_user(self, user: User) -> bool:
        with get_session() as session:
            # Verificar se o e-mail já existe
            existing_user = session.execute(
                select(users).where(users.c.email == user.email)
            ).fetchone()

            if existing_user:
                raise ValueError("Já existe um cadastro com esse e-mail")

            # Inserir novo usuário
            new_user = {
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "password": user.password,
                "fingerprint": user.fingerprint,
                "status": user.status,
                "uuid": user.uuid,
                "date": user.date,
            }
            session.execute(insert(users).values(**new_user))

            return True

    def auth_login(
        self, email: str, password: str, user_agent: str, ip: str
    ) -> Dict[str, Any]:
        with get_session() as session:
            # Verificar se o usuário existe e está ativo
            user_record = session.execute(
                select(users).where(users.c.email == email, users.c.status == True)
            ).fetchone()

            if not user_record:
                raise ValueError("Nenhum usuário encontrado")

            # Validar a senha
            if not bcrypt.checkpw(
                password.encode("utf-8"), user_record.password.encode("utf-8")
            ):
                raise ValueError("A senha está incorreta")

            # Revogar todas as sessões ativas do usuário
            session.execute(
                update(sessions)
                .where(
                    (sessions.c.user_uuid == user_record.uuid)
                    & (sessions.c.revoked == False)
                )
                .values(revoked=True)
            )

            # Gerar par de tokens usando o serviço
            token_pair = self.token_service.generate_token_pair(str(user_record.uuid))

            # Usar os hashes já calculados do TokenPair
            # Criar entidade de sessão
            user_session = Session(
                access_token=token_pair.access_token_hash,
                refresh_token=token_pair.refresh_token_hash,
                access_token_expires_at=token_pair.access_token_expires_at,
                refresh_token_expires_at=token_pair.refresh_token_expires_at,
                user_uuid=user_record.uuid,
                user_agent=user_agent,
                ip=ip,
            )

            # Salvar sessão no banco de dados
            session_data = {
                "access_token": user_session.access_token,
                "refresh_token": user_session.refresh_token,
                "access_token_expires_at": user_session.access_token_expires_at,
                "refresh_token_expires_at": user_session.refresh_token_expires_at,
                "user_agent": user_session.user_agent,
                "ip": user_session.ip,
                "user_uuid": user_session.user_uuid,
                "revoked": user_session.revoked,
                "type": user_session.type,
                "uuid": user_session.uuid,
                "date": user_session.date,
            }
            session.execute(insert(sessions).values(**session_data))

            return {
                "access_token": token_pair.access_token,
                "refresh_token": token_pair.refresh_token,
                "access_token_expires_at": token_pair.access_token_expires_at,
                "refresh_token_expires_at": token_pair.refresh_token_expires_at,
            }

    def revoke_session(self, refresh_token: str) -> bool:
        with get_session() as session:
            try:
                # Decodificar o refresh token permitindo tokens expirados
                payload = self.token_service.decode_token(
                    refresh_token, verify_exp=False
                )

                refresh_token_random = payload.get("refresh_token")

                if not refresh_token_random:
                    return False

                # Gerar hash do refresh token
                refresh_token_hash = self.token_service.hash_token(refresh_token_random)

                # Revogar a sessão específica
                result = session.execute(
                    update(sessions)
                    .where(sessions.c.refresh_token == refresh_token_hash)
                    .values(revoked=True)
                )

                return result.rowcount > 0

            except Exception:
                return False
