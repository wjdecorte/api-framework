# from pydantic_settings import BaseSettings
#
# from api_framework import app_settings
#
#
# class UserSettings(BaseSettings):
#     user_table_schema: str = app_settings.database_default_schema
#
#
# @lru_cache
# def get_user_settings():
#     return Settings()
#
#
# user_settings = get_user_settings()
