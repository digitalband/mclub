from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db.db_helper import db_helper
from schemas.auth import PayloadSchema
from services.auth import AuthService

DBSessionDependency = Annotated[AsyncSession, Depends(db_helper.get_session_dependency)]


def auth_service(session: DBSessionDependency) -> AuthService:
    return AuthService(
        private_key = settings.auth_jwt.private_key_path.read_text(),
        public_key = settings.auth_jwt.public_key_path.read_text(),
        algorithm = settings.auth_jwt.algorithm,
        verification_code_length=settings.auth_jwt.verification_code_length,
        session=session
    )


AuthDependency = Annotated[AuthService, Depends(auth_service)]


async def get_current_auth_user(
    auth_service: AuthDependency,
    token: str = Depends(APIKeyHeader(name="X-API-Key"))
) -> PayloadSchema:
    """Получает токен и возвращает его payload"""
    return await auth_service.validate_token(token)
