import logging
from logging.config import dictConfig
import traceback

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from testapi import app_settings
from testapi.exceptions import ALL_EXCEPTIONS
from testapi.migrations.alembic_runner import upgrade
from testapi.common.schemas import ValidationErrorSchema
from testapi.common.routers import router as common_router
from testapi.logger_conf import log_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # downgrade()
    # generate_revision(msg="enter Your message here")
    upgrade()
    yield


dictConfig(log_config)

app = FastAPI(
    openapi_url=f"{app_settings.base_url_prefix}/openapi.json",
    title="Test API",
    description="A API Framework for all API's",
    version=app_settings.version,
    docs_url=f"{app_settings.base_url_prefix}/docs",
    redoc_url=f"{app_settings.base_url_prefix}/redoc",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error",
            "model": ValidationErrorSchema,
        }
    },
    lifespan=lifespan,
)

logger = logging.getLogger(app_settings.logger_name)

logger.info("Register Routers")

app.include_router(
    common_router, prefix=f"{app_settings.base_url_prefix}/common/api/v1"
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, error):
    logger.debug(f"{request=}")
    logger.error(msg="api error", exc_info=error)
    if type(error).__name__ in ALL_EXCEPTIONS:
        d = dict(
            type=type(error).__name__,
            code=error.code,
            message=error.message,
            http_code=error.http_code,
        )
        http_code = error.http_code
    else:
        d = {
            "code": "testapi.error.999",
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }
        http_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    result = {"errors": [d]}
    response = JSONResponse(result)
    response.status_code = http_code
    return response
