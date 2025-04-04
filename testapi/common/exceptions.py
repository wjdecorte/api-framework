from dataclasses import dataclass

from testapi.exceptions import AppBaseError


@dataclass
class TestBaseError(AppBaseError):
    @property
    def code(self):
        return f"workflows.error.{self.error_number}"


@dataclass
class UserDoesNotExistError(TestBaseError):
    message: str = "User does not exist"
    http_code: int = 404


@dataclass
class UserAlreadyExistError(AppBaseError):
    message: str = "User already exists"
    http_code: int = 500
