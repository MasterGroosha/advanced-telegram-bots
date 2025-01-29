from pydantic import BaseModel, Extra

from database.config.orm.engine import EngineConfig
from database.config.orm.session import SessionConfig


class ORMConfig(BaseModel):
    engine: EngineConfig = EngineConfig()
    session: SessionConfig = SessionConfig()

    class Config:
        extra = Extra.allow
