from enum import StrEnum, IntEnum
from typing import Annotated

from pydantic import AfterValidator
from sqlmodel import Field, Relationship

from api_framework.common.models import AppBaseModel


class UserStatus(StrEnum):
    ACTIVE: str = "active"
    NONACTIVE: str = "nonactive"
    ERROR: str = "error"


class AddressType(IntEnum):
    HOME: int = 1
    WORK: int = 2
    OTHER: int = 3


def user_status_valid_values(value: str):
    if value not in UserStatus:
        raise ValueError(f"{value} is not a valid value")
    return value


def address_type_valid_values(value: int):
    if value not in AddressType:
        raise ValueError(f"{value} is not a valid value")
    return value


class UserBaseTableModel(AppBaseModel):
    __table_args__ = {"schema": "user_example"}


class User(UserBaseTableModel, table=True):
    username: str = Field(max_length=100, unique=True, nullable=False)
    description: str = Field(max_length=250, nullable=True)
    email: str = Field(max_length=250, nullable=True)
    first_name: str = Field(max_length=250, nullable=True)
    last_name: str = Field(max_length=250, nullable=True)
    addresses: list["UserAddress"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    phone_number: str = Field(max_length=20, nullable=True)
    status: Annotated[
        str,
        Field(max_length=15, nullable=False),
        AfterValidator(user_status_valid_values),
    ]


class UserAddress(UserBaseTableModel, table=True):
    type: Annotated[
        int,
        Field(nullable=False, unique=True),
        AfterValidator(address_type_valid_values),
    ]
    address_line_1: str = Field(max_length=250, nullable=False)
    address_line_2: str = Field(max_length=250, nullable=True)
    city: str = Field(max_length=250, nullable=False)
    state: str = Field(max_length=250, nullable=False)
    postal_code: str = Field(max_length=10, nullable=False)
    user_id: int = Field(
        foreign_key=f"{UserBaseTableModel.__table_args__.get('schema')}.user.id",
        nullable=False,
    )
    user: User = Relationship(back_populates="addresses")
