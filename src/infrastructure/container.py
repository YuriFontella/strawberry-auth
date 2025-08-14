"""
Container de dependências usando dependency-injector
"""

from dependency_injector import containers, providers
from src.infrastructure.config.settings import get_settings
from src.presentation.graphql.context import GraphQLContext
from src.presentation.graphql.user.resolver import UserResolvers
from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.services.token_service import TokenService
from src.infrastructure.database.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


class Container(containers.DeclarativeContainer):
    """Container de dependências da aplicação"""

    # Configurações
    settings = providers.Singleton(get_settings)

    # Serviços
    token_service = providers.Factory(
        TokenService,
        jwt_key=settings().jwt_secret_key,
        salt=settings().salt,
        access_token_expires_minutes=settings().access_token_expires_minutes,
        refresh_token_expires_days=settings().refresh_token_expires_days,
    )

    # Repositórios
    user_repository = providers.Singleton(
        SQLAlchemyUserRepository,
        token_service=token_service,
    )

    # Use Cases
    user_use_cases = providers.Factory(UserUseCases, user_repository=user_repository)

    # Resolvers
    user_resolvers = providers.Factory(UserResolvers, user_use_cases=user_use_cases)

    # Contexto GraphQL
    graphql_context = providers.Factory(
        GraphQLContext, settings=settings, user_resolvers=user_resolvers
    )
