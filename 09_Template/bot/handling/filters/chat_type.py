from enum import Enum

from aiogram.filters import BaseFilter
from aiogram.types import Chat, TelegramObject


class ChatType(str, Enum):
    private = 'private'
    group = 'group'
    supergroup = 'supergroup'
    channel = 'channel'


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: ChatType) -> None:
        super().__init__()
        self.chat_type = chat_type

    async def __call__(self, _: TelegramObject, event_chat: Chat) -> bool:
        if not event_chat:
            return False
        return event_chat.type == self.chat_type
