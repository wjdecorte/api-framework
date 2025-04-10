import logging

from fastapi import APIRouter

from api_framework import app_settings
from api_framework.common.middleware import LogRoute

router = APIRouter(
    tags=[
        "common",
    ],
    route_class=LogRoute,
)

logger = logging.getLogger(f"{app_settings.logger_name}.common")


@router.get("/healthcheck")
def get_healthcheck():
    logger.debug("Healthcheck")
    return {"msg": "Happy"}


@router.get("/info")
def get_info():
    return {
        k: v
        for k, v in app_settings.model_dump().items()
        if "password" not in k.lower()
    }
