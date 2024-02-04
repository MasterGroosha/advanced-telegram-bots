from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BIGINT, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from bot.db.base import Base


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class RegisteredUser(Base):
    __tablename__ = "registeredusers"

    telegram_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )
    registered_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=utcnow()
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="telegram_user",
        cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("registeredusers.telegram_id")
    )
    created_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=utcnow()
    )
    order_contents: Mapped[str] = mapped_column(
        TEXT,
        nullable=False
    )
    telegram_user: Mapped["RegisteredUser"] = relationship(
        back_populates="orders"
    )
