from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from src.infrastructure.container import Container
from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.session import create_tables
from src.presentation.graphql.schema import create_schema


def create_app() -> FastAPI:
    """Cria a aplicação FastAPI com Clean Architecture"""

    # Configurações
    settings = get_settings()

    # Container de dependências
    container = Container()

    # Criar tabelas do banco
    create_tables()

    # Schema GraphQL
    schema = create_schema()

    # Contexto do GraphQL
    async def get_context():
        return container.graphql_context()

    # GraphQL Router
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        subscription_protocols=[
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        ],
    )

    # Aplicação
    fastapi = FastAPI(debug=settings.debug)

    # Configuração CORS
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configuração de Trusted Hosts
    fastapi.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"]
    )

    # Configuração de GZip Middleware
    fastapi.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

    # Incluir rota GraphQL
    fastapi.include_router(graphql_app, prefix="/graphql")

    return fastapi


# Criar a aplicação
app = create_app()

if __name__ == "__main__":
    import uvicorn

    server = get_settings()
    uvicorn.run("main:app", host=server.host, port=server.port, reload=server.reload)
