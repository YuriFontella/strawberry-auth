import strawberry
from typing import AsyncGenerator
from fastapi import Request, Response
from strawberry.types import Info

from src.domain.auth.permissions import IsAuthenticated
from src.presentation.graphql.user.input import UserInput
from src.presentation.graphql.user.type import UserType


@strawberry.type
class UserQuery:
    """Query root for User"""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def current_user(self, info: Info) -> UserType:
        user = info.context.user
        return UserType(
            uuid=user.uuid,
            name=user.name,
            email=user.email,
            role=user.role,
            fingerprint=user.fingerprint,
            avatar=user.avatar,
            date=user.date,
            status=user.status,
        )


@strawberry.type
class UserMutation:
    """Mutation root for User"""

    @strawberry.mutation()
    def create_user(self, info: Info, data: UserInput) -> bool:
        context = info.context
        created_user = context.user_resolvers.create_user(
            name=data.name.strip(),
            email=data.email.strip(),
            password=data.password.strip(),
        )
        return created_user

    @strawberry.field()
    def auth_login(self, info: Info, email: str, password: str) -> bool:
        context = info.context
        request: Request = context.request
        response: Response = context.response
        user_agent = request.headers.get("user-agent")
        ip = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for")

        result = context.user_resolvers.auth_login(
            email=email.strip(), password=password.strip(), user_agent=user_agent, ip=ip
        )

        # Definir cookies de sessão (sem max_age)
        response.set_cookie(
            key="x-access-token",
            value=result["access_token"],
            # max_age = cookie de sessão
            httponly=True,
            secure=False,
            samesite="lax",
        )

        response.set_cookie(
            key="x-refresh-token",
            value=result["refresh_token"],
            # max_age = cookie de sessão
            httponly=True,
            secure=False,
            samesite="lax",
        )

        return True

    @strawberry.mutation()
    def logout(self, info: Info) -> bool:
        """Fazer logout e revogar a sessão"""
        context = info.context
        request: Request = context.request
        response: Response = context.response

        # Buscar refresh token no cookie
        refresh_token = request.cookies.get("x-refresh-token")

        if refresh_token:
            # Revogar a sessão no banco de dados
            context.user_resolvers.revoke_session(refresh_token)

        # Limpar cookies
        response.delete_cookie("x-access-token")
        response.delete_cookie("x-refresh-token")

        return True


@strawberry.type
class UserSubscription:
    """Subscription root for User"""

    @strawberry.subscription()
    async def notifications(self) -> AsyncGenerator[str, None]:
        yield "User notification!"
