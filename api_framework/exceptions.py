"""Defined exceptions for the api_framework Service"""

from dataclasses import dataclass
from typing import Dict, Type

ALL_EXCEPTIONS: Dict[str, Type] = {}


@dataclass
class AppBaseError(Exception):
    """App Base Exception"""

    message: str = "Base exception"
    http_code: int = 500

    @property
    def code(self):
        return f"api.error.{self.error_number}"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.error_number = f"{len(ALL_EXCEPTIONS):03}"
        ALL_EXCEPTIONS[cls.__name__] = cls


@dataclass
class TestError(AppBaseError):
    message: str = "Test exception"


@dataclass
class HTTPTestError(AppBaseError):
    http_code: int = 403


@dataclass
class InvalidValueError(AppBaseError):
    http_code: int = 400


@dataclass
class InvalidActionError(AppBaseError):
    message: str = "Invalid action provided"
    http_code: int = 400


@dataclass
class FileWriteError(AppBaseError):
    message: str = "Failed to write the file"
    http_code: int = 500


@dataclass
class ExecutionError(AppBaseError):
    http_code: int = 500


@dataclass
class AuthenticationError(AppBaseError):
    message: str = "Error occurred while fetching access token"
    http_code: int = 500


@dataclass
class UniqueColumnNotFoundError(AppBaseError):
    http_code: int = 500


@dataclass
class MissingConnectionDetailsError(AppBaseError):
    message: str = "Missing Connection details"
    http_code: int = 500
