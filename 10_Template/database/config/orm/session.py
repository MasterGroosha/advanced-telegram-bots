from pydantic import BaseModel, Extra


class SessionConfig(BaseModel):
    expire_on_commit: bool = False

    class Config:
        extra = Extra.allow
