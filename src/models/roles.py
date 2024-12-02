from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from models.mixins.user_relation import UserRelationMixin


class Role(Base, UserRelationMixin):
    __user_back_populates = "roles"

    title: Mapped[str] = mapped_column(String(8), unique=True)