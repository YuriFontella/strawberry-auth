from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import metadata
from src.infrastructure.config.settings import get_database_url
from sqlalchemy.pool import QueuePool


# Criar engine do banco de dados
engine = create_engine(
    url=get_database_url(),
    echo=False,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    pool_size=10,
    max_overflow=20,
)

# Criar session factory
SessionLocal = sessionmaker(expire_on_commit=False, bind=engine)


@contextmanager
def get_session():
    """Context manager para obter uma sessão do banco de dados"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """Cria todas as tabelas no banco de dados"""
    metadata.create_all(bind=engine)
