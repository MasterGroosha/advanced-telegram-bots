import asyncio

import os
import nats
import structlog
from nats.js.api import KeyValueConfig, ObjectStoreConfig


async def main():
    logger = structlog.get_logger(__name__)
    nc = await nats.connect(os.getenv("NATS_URL"))
    js = nc.jetstream()
    logger.debug('NATS connection established')
    # FSM buckets
    await js.create_key_value(KeyValueConfig("fsm_data_aiogram"))
    await js.create_key_value(KeyValueConfig("fsm_states_aiogram"))
    # Watermarker
    await js.create_key_value(KeyValueConfig("watermarker-tasks"))
    await js.create_key_value(KeyValueConfig("watermarker-done-tasks"))
    await js.create_object_store("watermarker-images", ObjectStoreConfig())
    logger.debug('NATS Buckets created')


if __name__ == '__main__':
    asyncio.run(main())
