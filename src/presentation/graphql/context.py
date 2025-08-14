"""
Contexto GraphQL com acesso aos objetos Request e Response
"""

from strawberry.fastapi import BaseContext
from dataclasses import dataclass
from src.infrastructure.config.settings import Settings
from src.presentation.graphql.user.resolver import UserResolvers


@dataclass
class GraphQLContext(BaseContext):
    """Contexto GraphQL que inclui request, response e configurações"""

    settings: Settings
    user_resolvers: UserResolvers
