import io
from typing import Annotated

from aiogram import Bot
from aiogram.types import BufferedInputFile
from faststream import context, Context, FastStream, Logger
from faststream.nats import JStream, NatsBroker, NatsMessage, PullSub, NatsRouter
from nats.js.api import DeliverPolicy
from nats.js.errors import ObjectNotFoundError

from bot.payload.convert_task import Task

router = NatsRouter()

stream = JStream(name="KV_watermarker-done-tasks", declare=False)

@router.subscriber(
    "$KV.watermarker-done-tasks.{img_uuid}",
    stream=stream,
    deliver_policy=DeliverPolicy("new"),
    durable="True",
    pull_sub=PullSub(batch_size=10),
    retry=True,
    filter=lambda msg: msg.headers.get("KV-Operation") is None,
)

async def handler(task: Task, logger: Logger, msg: NatsMessage, broker: Annotated[NatsBroker, Context("broker")], bot: Bot = Context()):
    logger.info(task.img_uuid)

    # todo Unresolved reference broker
    images = await broker.object_storage("watermarker-images", declare=False)
    tasks = await broker.key_value("watermarker-tasks", declare=False)
    done_tasks = await broker.key_value("watermarker-done-tasks", declare=False)

    buf = io.BytesIO()
    await images.get("out-" + str(task.img_uuid), buf)
    await done_tasks.delete(str(task.img_uuid))
    await tasks.delete(str(task.img_uuid))
    try:
        await images.delete(str(task.img_uuid))
    except ObjectNotFoundError:
        pass
    await bot.send_photo(task.chat_id,
                         photo=BufferedInputFile(
                             file=buf.getvalue(),
                             filename=task.watermark
                         )
    )

@router.subscriber(
    "$KV.watermarker-done-tasks.{img_uuid}",
    stream=stream,
    deliver_policy=DeliverPolicy("new"),
    durable="True",
    pull_sub=PullSub(batch_size=10),
    retry=True,
    filter=lambda msg: msg.headers.get("KV-Operation") is not None,
)
async def trash(data: bytes, msg: NatsMessage):
    await msg.ack()

async def run(bot: Bot, nats_address: str):
    broker = NatsBroker(nats_address)
    app = FastStream(broker)
    broker.include_router(router)
    context.set_global("bot", bot)  # Globals is shit!
    await app.run()
