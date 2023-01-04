import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings

DEFAULT_CONFIG_PATH = Path.home().joinpath(".sunat_api/config")


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    env_config_path = os.getenv("SUNAT_API_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))

    config_path = Path(env_config_path)

    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        config_path.write_text("", encoding=encoding)

    config_text = config_path.read_text(encoding)
    if not config_text:
        return {}
    return json.loads(config_text)


class Settings(BaseSettings):
    BASE_AUTH_URL: str = "https://api-seguridad.sunat.gob.pe"
    BASE_URL: str = "https://api-cpe.sunat.gob.pe"
    LOG_LEVEL: str = "INFO"
    CONFIG_PATH: Path = DEFAULT_CONFIG_PATH
    CLIENT_ID: Optional[str] = None
    CLIENT_SECRET: Optional[str] = None
    USER: Optional[str] = None
    PASSWORD: Optional[str] = None

    class Config:
        env_prefix = "SUNAT_API_"
        env_file_encoding = "utf-8"
        env_file = ".env"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )


settings = Settings()
