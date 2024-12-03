from typing import TYPE_CHECKING

from sqlalchemy import func, String, LargeBinary, Boolean, DateTime, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.roles import Role
    from models.session import Session


class User(Base):
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='True')
    created_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now()
    )
    role: Mapped[list["Role"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
