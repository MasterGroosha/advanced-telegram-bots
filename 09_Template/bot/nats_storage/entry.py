import asyncio
import json
from typing import Any, Dict, Optional

import structlog
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey
from nats.js.errors import KeyNotFoundError, NotFoundError
from nats.js.kv import KeyValue


class NATSFSMStorage(BaseStorage):
    def __init__(
        self,
        kv_states: KeyValue,
        kv_data: KeyValue,
        serializer=json.dumps,
        deserializer=json.loads,
    ):
        super().__init__()
        self.kv_states = kv_states
        self.kv_data = kv_data
        self.serializer = serializer
        self.deserializer = deserializer
        self.logger = structlog.get_logger(__name__)

    @staticmethod
    def _key_formatter(key: StorageKey) -> str:
        return (
            (
                f'{key.bot_id}.{key.user_id}.{key.chat_id}.{key.destiny}'
                + (f'.{key.thread_id}' if key.thread_id else '')
            )
            .replace(':', '.')
            .rstrip('.')
        )

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        state = state.state if isinstance(state, State) else state
        ser_state = self.serializer(state or None)
        await self.kv_states.put(self._key_formatter(key), ser_state.encode())

    async def get_state(self, key: StorageKey) -> Optional[str]:
        try:
            entry = await self.kv_states.get(self._key_formatter(key))
            data = self.deserializer(entry.value)
        except NotFoundError:
            return None
        return data

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        await self.kv_data.put(self._key_formatter(key), self.serializer(data) if data else b'')

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        try:
            entry = await self.kv_data.get(self._key_formatter(key))
            if entry.value is None:
                return {}
            return self.deserializer(entry.value)
        except KeyNotFoundError:
            return {}

    async def close(self) -> None:
        await asyncio.gather(self.kv_data.purge_deletes(),self.kv_states.purge_deletes())
        return None
