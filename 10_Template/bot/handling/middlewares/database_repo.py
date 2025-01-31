from typing import Any, Awaitable, Callable, Dict, Optional

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker


class DatabaseMiddleware(BaseMiddleware):
    """Middleware which drops session into a context."""

    def __init__(
            self,
            session_factory: Optional[sessionmaker | str],
            context_name: str = 'db',
    ) -> None:
        self.context_name = context_name
        if isinstance(session_factory, str):
            self.session_factory = None
            self.session_factory_ctx_name = session_factory
        else:
            self.session_factory = session_factory
        self.logger = structlog.getLogger()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            ctx_data: Dict[str, Any],
    ) -> None:
        await self.logger.debug('DatabaseMiddleware begun')
        session_factory = self.session_factory or ctx_data.get(
            self.session_factory_ctx_name
        )
        async with session_factory() as session:  # type: ignore
            ctx_data[self.context_name] = session
            try:
                await handler(event, ctx_data)
                await session.commit()
            except Exception as exception:
                await session.rollback()
                raise exception
        ctx_data.pop(self.context_name, None)
        await self.logger.debug('DatabaseMiddleware end')
