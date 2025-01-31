from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.logger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        event_handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        ctx_data: Dict[str, Any],
    ) -> None:
        start_time = datetime.now()
        structlog.contextvars.bind_contextvars(
            update=event.model_dump(
                exclude_unset=True,
                exclude_none=True,
                exclude_defaults=True,
            ),
            start_time=datetime.now(),
        )
        try:
            await event_handler(event, ctx_data)
        except Exception as e:
            end_time = datetime.now()
            await self.logger.exception(
                'Abnormal handling event detected, critical error happened',
                e,
                start_time=start_time,
                end_time=end_time,
                execution_time=(end_time - start_time).microseconds,
            )
        else:
            end_time = datetime.now()
            execution_time = end_time - start_time
            await self.logger.info(
                f'Event successfully executed in {execution_time.microseconds} microseconds',
                execution_time=execution_time,
            )
        finally:
            structlog.contextvars.clear_contextvars()
