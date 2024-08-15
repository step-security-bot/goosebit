from pathlib import Path
from typing import Annotated, Iterable

from pydantic import BaseModel, BeforeValidator, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from goosebit.permissions import Permissions, PermissionsBase

from .const import BASE_DIR, LOGGING_DEFAULT, PWD_CXT


def parse_permissions(items: Iterable[str]):
    permissions = set()
    for p in items:
        permissions.update(Permissions.from_str(p))
    return permissions


class User(BaseModel):
    username: str
    hashed_pwd: Annotated[str, BeforeValidator(PWD_CXT.hash)] = Field(validation_alias="password")
    permissions: Annotated[set[PermissionsBase], BeforeValidator(parse_permissions)]

    def get_json_permissions(self):
        return [str(p) for p in self.permissions]


class PrometheusSettings(BaseModel):
    enable: bool = False
    port: int = 9090


class MetricsSettings(BaseModel):
    prometheus: PrometheusSettings = PrometheusSettings()


class GooseBitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GOOSEBIT_")

    artifacts_dir: Path = BASE_DIR.joinpath("artifacts")

    tenant: str = "DEFAULT"

    poll_time_default: str = "00:01:00"
    poll_time_updating: str = "00:00:05"
    poll_time_registration: str = "00:00:10"

    users: list[User] = []

    db_uri: str = f"sqlite:///{BASE_DIR.joinpath('db.sqlite3')}"

    metrics: MetricsSettings = MetricsSettings()

    logging: dict = LOGGING_DEFAULT

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls, BASE_DIR.parent.joinpath("settings.yaml")),
            env_settings,
            file_secret_settings,
        )
