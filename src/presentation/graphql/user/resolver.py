from dataclasses import dataclass
from typing import Dict, Any
from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.entities.user import User


@dataclass
class UserResolvers:
    user_use_cases: UserUseCases

    def create_user(self, name: str, email: str, password: str) -> bool:
        user = User(name=name, email=email, password=password)
        return self.user_use_cases.create_user(user)

    def auth_login(
        self, email: str, password: str, user_agent: str, ip: str
    ) -> Dict[str, Any]:
        return self.user_use_cases.auth_login(
            email=email, password=password, user_agent=user_agent, ip=ip
        )

    def revoke_session(self, refresh_token: str) -> bool:
        return self.user_use_cases.revoke_session(refresh_token)
