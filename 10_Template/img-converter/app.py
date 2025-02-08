import asyncio
import os
from uuid import UUID

from faststream import FastStream, Logger
from faststream.nats import JStream, NatsBroker, NatsMessage, PullSub
from nats.js.api import DeliverPolicy
from nats.js.errors import  ObjectNotFoundError
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

import io

broker = NatsBroker(os.getenv("NATS_URL"))  # "nats://nats:4222"
app = FastStream(broker)

stream = JStream(name="KV_watermarker-tasks", declare=False)

class Task(BaseModel):
    chat_id: int = Field()
    img_uuid: UUID = Field()
    img_format: str = Field()
    watermark: str = Field()

@broker.subscriber(
    "$KV.watermarker-tasks.{img_uuid}",
    stream=stream,
    deliver_policy=DeliverPolicy("new"),
    durable="True",
    pull_sub=PullSub(batch_size=10),
    retry=True,
    filter=lambda msg: msg.headers.get("KV-Operation") is None,
)
async def handler(task: Task, logger: Logger, msg: NatsMessage):
    logger.info(task.img_uuid)
    images = await broker.object_storage("watermarker-images", declare=False)
    done_tasks = await broker.key_value("watermarker-done-tasks", declare=False)
    buf = io.BytesIO()
    try:
        await images.get("in-" + str(task.img_uuid), buf)
    except ObjectNotFoundError:
        logger.info("Nack waiting for image to be uploaded")
        await msg.nack(1)
        return
    image = Image.open(io.BytesIO(buf.getbuffer()))
    width, height = image.size
    position = (width / 2, height / 2)
    img_fraction = 0.80
    breakpoint = width * img_fraction
    jumpsize = 50
    fontsize = 10
    font = ImageFont.truetype("font.otf", size=fontsize)

    while True:
        size = font.getbbox(task.watermark)
        width = size[2]-size[0]
        if width < breakpoint:
            fontsize += jumpsize
        else:
            jumpsize = jumpsize // 2
            fontsize -= jumpsize
        font = ImageFont.truetype("font.otf", size=fontsize)
        if jumpsize <= 2:
            break

    draw = ImageDraw.Draw(image)
    draw.text(position, task.watermark, font=font, fill=(240, 10, 10), anchor="mm", align="center")
    export_buf = io.BytesIO()
    image.save(export_buf, format=task.img_format.upper())
    await images.put("out-" + str(task.img_uuid), export_buf.getvalue())
    await done_tasks.create(str(task.img_uuid), msg.body)

@broker.subscriber(
    "$KV.watermarker-tasks.{img_uuid}",
    stream=stream,
    deliver_policy=DeliverPolicy("new"),
    durable="True",
    pull_sub=PullSub(batch_size=10),
    retry=True,
    filter=lambda msg: msg.headers.get("KV-Operation") is not None,
)
async def trash(data: bytes, msg: NatsMessage):
    await msg.ack()

if __name__ == "__main__":
    asyncio.run(app.run())
