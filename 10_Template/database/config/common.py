from typing import Optional

from pydantic import Extra, SecretStr

from database.config import BaseDBConfig
from database.config.orm.mixin import ORMConfig


class Config(BaseDBConfig):
    """Configuration for a common databases like PostgreSQL"""

    db_type: SecretStr = SecretStr('postgresql')
    db_name: SecretStr
    adapter: Optional[str]
    username: SecretStr
    password: SecretStr
    host: SecretStr  # port included! example: 'localhost:5432'
    orm: ORMConfig = ORMConfig()
    timeout: int = 60

    @property
    def uri(self) -> str:  # noqa: WPS210 type: ignore
        db_type = self.db_type.get_secret_value()
        db_name = self.db_name.get_secret_value()
        username = self.username.get_secret_value()
        password = self.password.get_secret_value()
        host = self.host.get_secret_value()
        adapter = f'+{self.adapter}' if self.adapter else ''
        return f'{db_type}{adapter}://{username}:{password}@{host}/{db_name}'  # noqa: WPS221

    class Config:
        extra = Extra.allow
