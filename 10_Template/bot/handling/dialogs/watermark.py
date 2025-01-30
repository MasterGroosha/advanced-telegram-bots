import io
import uuid
from typing import TYPE_CHECKING

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.text import Format
from fluentogram import TranslatorRunner
from nats.js import JetStreamContext
from structlog import get_logger

from bot.handling.states import Watermark
from bot.payload.convert_task import Task

logger = get_logger(__name__)


async def getter(dialog_manager: DialogManager, i18n: TranslatorRunner, **kwargs):
    await logger.debug('main page getter called')
    return {
        'enter_image': i18n.enter_image(),
        'enter_watermark': i18n.enter_watermark(),
    }

async def document_handler(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager,
):
    nc = manager.middleware_data["nc"]
    js: JetStreamContext = nc.jetstream()
    tasks = await js.key_value("watermarker-tasks")
    watermark = manager.find("watermark").get_value()
    while True:
        try:
            photo_uuid = uuid.uuid4()
            task = Task(chat_id=message.chat.id, img_uuid=photo_uuid, img_format="JPEG", watermark=watermark)
            await tasks.create(str(photo_uuid), task.model_dump_json().encode())
            break
        finally:
            pass
    obj = await js.object_store("watermarker-images")
    photo_io = io.BytesIO()
    photo_id = message.photo.pop().file_id
    await message.bot.download(photo_id, destination=photo_io)
    await obj.put("in-" + str(photo_uuid), photo_io.getvalue())
    print(manager.dialog_data)
    i18n = manager.middleware_data.get("i18n")
    await message.answer(i18n.in_progress())
    await manager.done()

dialog = Dialog(
    Window(
        Format('{enter_watermark}'),
        TextInput(id="watermark", on_success=Next()),
        state=Watermark.enter_text,
        getter=getter,
    ),
    Window(
        Format('{enter_image}'),
        MessageInput(document_handler, content_types=[ContentType.PHOTO]),
        state=Watermark.enter_photo,
        getter=getter,
    )
)
