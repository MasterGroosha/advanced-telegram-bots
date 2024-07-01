from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Integer, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db import Base
from bot.db.models.mixins import TimestampMixin


class Game(TimestampMixin, Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # created_at добавляется из миксина

    user: Mapped["User"] = relationship(back_populates="games")