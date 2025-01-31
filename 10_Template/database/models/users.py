from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True, nullable=False)
    lang: Mapped[str] = mapped_column(Text, default="en", nullable=False)
