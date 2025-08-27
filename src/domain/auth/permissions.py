from uuid import UUID
from strawberry.types import Info
from strawberry.permission import BasePermission
from fastapi import Request, Response
from dataclasses import dataclass, field
from sqlalchemy import select
from src.infrastructure.database.session import get_session
from src.infrastructure.database.models import users, sessions
from src.domain.services.token_service import TokenService
from src.domain.entities.user import User


@dataclass
class IsAuthenticated(BasePermission):
    message: str = "User is not authenticated"
    error_extensions: dict = field(default_factory=lambda: {"code": "UNAUTHORIZED"})

    def has_permission(self, source: object, info: Info, **kwargs) -> bool:
        context = info.context
        request: Request = context.request
        response: Response = context.response

        try:
            # Serviço de token
            token_service = TokenService(
                context.settings.jwt_secret_key,
                context.settings.salt,
                context.settings.access_token_expires_minutes,
                context.settings.refresh_token_expires_days,
            )

            # Cookies
            access_token = request.cookies.get("x-access-token")
            refresh_token = request.cookies.get("x-refresh-token")

            if not access_token:
                self.message = "Authentication cookie missing or invalid"
                return False

            # Decodificar o access token permitindo tokens expirados
            payload = token_service.decode_token(access_token, verify_exp=False)
            if not payload or payload.get("type") != "access":
                self.message = "Invalid token"
                return False

            # Verificar se o access token não expirou
            if not token_service.is_token_valid(payload):

                def handle_token_failure(message_failure):
                    """Trata falhas de token limpando cookies e definindo mensagem de erro"""

                    self.message = message_failure
                    response.delete_cookie("x-access-token")
                    response.delete_cookie("x-refresh-token")
                    return False

                # Token expirado, tentar renovar com refresh token
                if not refresh_token:
                    return handle_token_failure(
                        "Access token expired and no refresh token provided"
                    )

                # Tentar renovar access token
                new_access_token = token_service.refresh_token(
                    refresh_token, access_token
                )
                if not new_access_token:
                    return handle_token_failure("Failed to refresh token")

                # Definir o novo cookie do access token
                response.set_cookie(
                    key="x-access-token",
                    value=new_access_token.access_token_jwt,
                    # max_age = cookie de sessão
                    httponly=True,
                    secure=False,
                    samesite="strict",
                )

                # Decodificar o NOVO access token para usar os dados atualizados
                payload = token_service.decode_token(new_access_token.access_token_jwt)
                if not payload:
                    self.message = "Failed to decode new access token"
                    return False

            user_uuid = payload.get("uuid")
            if not user_uuid:
                self.message = "Invalid uuid token payload"
                return False

            # Gerar hash do access_token usando o serviço
            access_token_value = payload.get("access_token")
            if not access_token_value:
                self.message = "Invalid access token payload"
                return False

            access_token_hash = token_service.hash_token(access_token_value)

            # Buscar sessão no banco
            with get_session() as session:
                base_query = (
                    select(
                        users.c.uuid,
                        users.c.name,
                        users.c.email,
                        users.c.role,
                        users.c.fingerprint,
                        users.c.status,
                        users.c.avatar,
                        users.c.date,
                    )
                    .select_from(
                        users.join(sessions, users.c.uuid == sessions.c.user_uuid)
                    )
                    .where(
                        (users.c.uuid == UUID(user_uuid))
                        & (sessions.c.access_token == access_token_hash)
                        & (sessions.c.revoked.is_(False))
                        & (users.c.status.is_(True))
                    )
                )
                result = session.execute(base_query).fetchone()

                if not result:
                    self.message = "User not found or session invalid"
                    return False

            # Armazena o usuário atual no contexto como entidade User
            info.context.user = User(
                uuid=result.uuid,
                name=result.name,
                email=result.email,
                role=result.role,
                fingerprint=result.fingerprint,
                avatar=result.avatar,
                date=result.date,
                status=result.status,
            )
            return True

        except Exception as e:
            print(f"Authentication error: {e}")
            self.message = f"Authentication error: {str(e)}"
            return False
