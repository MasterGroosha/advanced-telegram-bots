from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.state import State
from aiogram.types import TelegramObject, Update
from aiogram_dialog import StartMode
from aiogram_dialog.api.exceptions import UnknownIntent
from structlog import get_logger


class DialogResetMiddleware(BaseMiddleware):
    def __init__(self, init_state: State, mode: StartMode) -> None:
        self.init_state = init_state
        self.mode = mode
        self.logger = get_logger(self.__class__.__name__)

    async def __call__(
        self,
        event_handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        ctx_data: Dict[str, Any],
    ) -> None:
        await self.logger.debug('DialogResetMiddleware begun')
        try:
            await event_handler(event, ctx_data)
        except UnknownIntent:
            await self.logger.info(f'Unknown intent {type(ctx_data)}')
            manager = ctx_data.get('dialog_manager')
            if manager:
                await manager.start(self.init_state, mode=self.mode)
            await event.callback_query.answer()
        await self.logger.debug('DialogResetMiddleware end')
