from dataclasses import dataclass

from api_framework.exceptions import AppBaseError


@dataclass
class CommonBaseError(AppBaseError):
    @property
    def code(self):
        return f"common.error.{self.error_number}"
