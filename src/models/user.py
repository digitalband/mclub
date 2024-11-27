from sqlalchemy import func, String, LargeBinary, Boolean, DateTime, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

class User(Base):
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(8), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='True')
    created_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now()
    )
