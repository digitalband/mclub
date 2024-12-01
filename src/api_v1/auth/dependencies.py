from typing import Annotated

from fastapi import Depends

from api_v1.auth.services import AuthService
from core.config import settings


def auth_service() -> AuthService:
    return AuthService(
        private_key = settings.auth_jwt.private_key_path.read_text(),
        public_key = settings.auth_jwt.public_key_path.read_text(),
        algorithm = settings.auth_jwt.algorithm,
        verification_code_length=settings.auth_jwt.verification_code_length
    )


AuthDependency = Annotated[AuthService, Depends(auth_service)]