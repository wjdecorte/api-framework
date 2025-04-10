from fastapi import Header

# from sqlalchemy.ext.asyncio import create_async_engine, async_session
from sqlalchemy import create_engine
from sqlmodel import Session

from api_framework import app_settings


class CommonHeaders:
    def __init__(
        self,
        x_auth_key: str | None = Header(None),  # noqa: B008
        x_tenant_id: str | None = Header(None),  # noqa: B008
    ):
        self.auth_key = x_auth_key
        self.tenant_id = x_tenant_id


# if "asyncpg" in app_settings.database_url:
#     from sqlalchemy.ext.asyncio import create_async_engine, async_session
#     engine = create_async_engine(database_url=app_settings.database_url)
# else:

engine = create_engine(
    url=app_settings.database_url.format(pswd=app_settings.database_password), echo=True
)


def get_session():
    with Session(engine) as session:
        yield session
