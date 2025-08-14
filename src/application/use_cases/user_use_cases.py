import bcrypt
from dataclasses import dataclass
from typing import Dict, Any
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


@dataclass
class UserUseCases:
    user_repository: UserRepository

    def create_user(self, user: User) -> bool:
        # Validar campos obrigatórios
        user.validate()

        # Hash da senha antes de enviar para o repositório
        if user.password:
            user.password = bcrypt.hashpw(
                user.password.encode("utf-8"), bcrypt.gensalt(10)
            ).decode("utf-8")
        return self.user_repository.create_user(user)

    def auth_login(
        self, email: str, password: str, user_agent: str, ip: str
    ) -> Dict[str, Any]:
        return self.user_repository.auth_login(
            email=email, password=password, user_agent=user_agent, ip=ip
        )

    def revoke_session(self, refresh_token: str) -> bool:
        return self.user_repository.revoke_session(refresh_token)
