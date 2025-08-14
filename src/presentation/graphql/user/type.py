import strawberry
from src.domain.entities.user import User


@strawberry.type
class UserType(User):
    """Tipo GraphQL para User"""
