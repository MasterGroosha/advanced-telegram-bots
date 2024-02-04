from os import getenv
from pathlib import Path

from pydantic import BaseModel, SecretStr
from yaml import load

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


class Settings(BaseModel):
    bot_token: SecretStr


def parse_settings() -> Settings:
    env_var = "BOT_CONFIG_FILE"

    file_path = getenv(env_var)
    if file_path is None:
        error = f"Environment variable {env_var} is missing or empty"
        raise ValueError(error)

    if not Path(file_path).is_file():
        error = f"Path {file_path} is not a file or doesn't exist"
        raise ValueError(error)

    with open(file_path, "rt") as file:
        config_data = load(file, SafeLoader)

    return Settings.model_validate(config_data)
