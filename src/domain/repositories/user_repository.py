from abc import ABC, abstractmethod
from src.domain.entities.user import User
from typing import Dict, Any


class UserRepository(ABC):
    """Interface para o repositório de usuários"""

    @abstractmethod
    def create_user(self, user: User) -> bool:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    def auth_login(
        self, email: str, password: str, user_agent: str, ip: str
    ) -> Dict[str, Any]:
        """Autentica o usuário e retorna tokens"""
        pass

    @abstractmethod
    def revoke_session(self, refresh_token: str) -> bool:
        """Revoga uma sessão específica usando o refresh token"""
        pass
