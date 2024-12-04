from sqlalchemy import String, TIMESTAMP, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from models.mixins.user_relation import UserRelationMixin


class Session(Base, UserRelationMixin):
    _user_back_populates = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now()
    )
    expires_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False
    )