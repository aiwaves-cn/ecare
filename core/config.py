import logging
from pathlib import Path
from typing import Type, Optional

from pydantic import BaseModel, ValidationError, HttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    PydanticBaseSettingsSource,
)

logger = logging.getLogger(__name__)

BASEDIR = Path(__file__).absolute().parent.parent
STATIC_DIR = BASEDIR.joinpath("static")
class MysqlSettings(BaseModel):
    db_url: str
    engine_args: Optional[dict] = {"pool_recycle": 3600}
    session_args: dict = {"expire_on_commit": False}


class RedisSettings(BaseModel):
    url: str

class Settings(BaseSettings):
    app_name: Optional[str]
    namespace: str = "local"
    version: str = "v1.2"

    # file_url: str

    # app: AppSettings = AppSettings()
    # hermes: HermesSettings
    # jwt: JWTSettings

    # xfyun: XfyunSettings
    # openai: OpenAISettings
    # zhipu: OpenAISettings
    # volcengine: VolcengineSettings
    # dingtalk: DingTalkSettings
    # knowledge: KnowledgeSettings

    mysql: MysqlSettings
    redis: RedisSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
        env_file=BASEDIR.joinpath(".env"),
        # yaml_file=BASEDIR.joinpath("configs/default.yaml"),
    )
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        """
        返回顺序即优先级顺序
        从高到低依次为：环境变量，dot变量，yaml文件、默认值
        """
        return (
            env_settings,
            dotenv_settings,
            # YamlConfigSettingsSource(settings_cls),
            init_settings,
        )


try:
    settings = Settings()
except ValidationError as e:
    logging.basicConfig(level=logging.INFO)
    logger.error("Init Settings Error")
    logger.error(e)