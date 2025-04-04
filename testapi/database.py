from sqlalchemy import create_engine

# from sqlalchemy.ext.asyncio import create_async_engine, async_session
from sqlmodel import Session

from testapi import app_settings

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
