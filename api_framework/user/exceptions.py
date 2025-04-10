from dataclasses import dataclass

from api_framework.common.exceptions import CommonBaseError
from api_framework.exceptions import AppBaseError


@dataclass
class UserDoesNotExistError(CommonBaseError):
    message: str = "User does not exist"
    http_code: int = 404


@dataclass
class UserAlreadyExistError(AppBaseError):
    message: str = "User already exists"
    http_code: int = 500
