from pydantic import BaseModel, Extra


class EngineConfig(BaseModel):
    class Config:
        extra = Extra.allow
