from importlib.metadata import version
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    version: str = version("api_framework")
    aws_default_region: str = "us-east-1"
    aws_endpoint_url: str | None = None
    base_url_prefix: str = "/framework/api/v1"
    title: str | None = "API Framework"
    description: str | None = "A API Framework for all API's"
    debug_mode: bool = False
    database_url: str = "test"
    database_password: str = "<PASSWORD>"
    database_default_schema: str = "common"
    api_log_type: str = "json"
    logger_name: str = "api-logger"
    log_level: str = "INFO"
    standard_log_format: str = "[%(asctime)s] [%(process)s] [%(name)s:%(module)s:%(funcName)s] [%(levelname)s]  %(message)s"
    json_log_format: str = """{
        "Name":            "name",
        "Levelno":         "levelno",
        "Levelname":       "levelname",
        "Pathname":        "pathname",
        "Filename":        "filename",
        "Module":          "module",
        "Lineno":          "lineno",
        "FuncName":        "funcName",
        "Created":         "created",
        "Asctime":         "asctime",
        "Process":         "process",
        "Message":         "message"
    }"""


@lru_cache
def get_app_settings():
    return Settings()


app_settings = get_app_settings()
