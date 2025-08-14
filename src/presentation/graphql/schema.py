import strawberry
from strawberry.tools import merge_types
from strawberry.schema.config import StrawberryConfig
from src.presentation.graphql.user.schema import (
    UserQuery,
    UserMutation,
    UserSubscription,
)


# Combine os tipos usando merge_types
Query = merge_types("Query", (UserQuery,))
Mutation = merge_types("Mutation", (UserMutation,))
Subscription = merge_types("Subscription", (UserSubscription,))


def create_schema() -> strawberry.Schema:
    """Cria o schema GraphQL federado"""
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        config=StrawberryConfig(auto_camel_case=False),
    )
