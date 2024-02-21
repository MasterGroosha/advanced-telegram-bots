from os import getenv
from pathlib import Path

from pydantic import BaseModel, SecretStr, PostgresDsn
from yaml import load

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


class Settings(BaseModel):
    bot_token: SecretStr
    db_url: PostgresDsn


def parse_settings() -> Settings:
    # Название переменной окружения,
    # значение которой есть путь к файлу конфигурации для процесса
    env_var = "BOT_CONFIG_FILE"

    file_path = getenv(env_var)
    # Если переменная окружения не задана, ошибка.
    if file_path is None:
        error = f"Environment variable {env_var} is missing or empty"
        raise ValueError(error)

    # Если переменная окружения задана, но такого файла нет, ошибка.
    if not Path(file_path).is_file():
        error = f"Path {file_path} is not a file or doesn't exist"
        raise ValueError(error)

    # Чтение файла и его парсинг библиотекой pyyaml
    with open(file_path, "rt") as file:
        config_data = load(file, SafeLoader)

    # Возвращается объект класса Settings
    return Settings.model_validate(config_data)
