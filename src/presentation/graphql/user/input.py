import strawberry

from src.domain.entities.user import User


@strawberry.input
class UserInput(User):
    """Input GraphQL para User"""
