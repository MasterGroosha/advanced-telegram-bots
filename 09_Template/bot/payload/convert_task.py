from uuid import UUID

from pydantic import BaseModel, Field


class Task(BaseModel):
    chat_id: int = Field()
    img_uuid: UUID = Field()
    img_format: str = Field()
    watermark: str = Field()
