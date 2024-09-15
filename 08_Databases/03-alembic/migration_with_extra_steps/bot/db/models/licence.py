from datetime import datetime, timedelta

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.db import Base


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )
