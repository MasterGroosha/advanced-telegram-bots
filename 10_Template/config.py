from dynaconf import Dynaconf
from pydantic import BaseModel

from bot.config import BotConfig as TgBotConfig
from database.config.common import Config as RelationalDatabaseConfig
from logs.config import Config as LoggingConfig

class NatsConfig(BaseModel):
    address: str

    class Config:
        extras = 'allow'


class Config(BaseModel):
    bot: TgBotConfig
    db: RelationalDatabaseConfig
    logging: LoggingConfig
    nats: NatsConfig

    class Config:
        alias_generator = str.upper


def parse_config():
    settings = Dynaconf(
        envvar_prefix='APP_CONF',
        settings_files=['settings.toml', '.secrets.toml'],
    )
    return Config.model_validate(settings.as_dict())
