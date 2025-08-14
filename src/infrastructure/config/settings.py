import os
import dotenv
from dataclasses import dataclass

dotenv.load_dotenv()


@dataclass
class Settings:
    """Configurações da aplicação"""

    jwt_secret_key: str
    salt: str
    access_token_expires_minutes: int
    refresh_token_expires_days: int
    debug: bool = False
    cors_origins: list = None
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


def get_database_url() -> str:
    """Obtém a URL do banco de dados"""
    return os.getenv("DATABASE_URL", "sqlite:///./app.db")


def get_settings() -> Settings:
    """Obtém as configurações da aplicação"""
    return Settings(
        debug=os.getenv("DEBUG", "True").lower() == "true",
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY", "your-secret-key-change-in-production"
        ),
        salt=os.getenv("SALT", "your-salt-change-in-production"),
        access_token_expires_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "15")
        ),
        refresh_token_expires_days=int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7")),
        cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "True").lower() == "true",
    )
