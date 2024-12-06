from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.db_helper import db_helper
from services.user import UserService

DBSessionDependency = Annotated[AsyncSession, Depends(db_helper.get_session_dependency)]


def user_service(session: DBSessionDependency) -> UserService:
    return UserService(session)


UserDependency = Annotated[UserService, Depends(user_service)]
