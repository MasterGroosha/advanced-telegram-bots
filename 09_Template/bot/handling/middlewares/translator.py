from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from fluentogram import TranslatorHub
from structlog import get_logger


class TranslatorRunnerMiddleware(BaseMiddleware):
    def __init__(
        self,
        translator_hub_alias: str = '_translator_hub',
        translator_runner_alias: str = 'i18n',
    ):
        self.translator_hub_alias = translator_hub_alias
        self.translator_runner_alias = translator_runner_alias
        self.logger = get_logger('TranslatorRunnerMiddleware')

    async def __call__(
        self,
        event_handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        ctx_data: Dict[str, Any],
    ) -> None:
        await self.logger.debug('TranslatorRunnerMiddleware begun')
        from_user = getattr(event, 'from_user', None)
        translator_hub: Optional[TranslatorHub] = ctx_data.get(self.translator_hub_alias)
        if from_user is None or translator_hub is None:
            return await event_handler(event, ctx_data)
        lang = from_user.language_code
        ctx_data[self.translator_runner_alias] = translator_hub.get_translator_by_locale(lang)
        await event_handler(event, ctx_data)
        await self.logger.debug('TranslatorRunnerMiddleware end')
