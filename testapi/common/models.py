from datetime import datetime
from enum import StrEnum, IntEnum
from typing import Annotated

from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, Relationship
from pydantic import AfterValidator, ConfigDict
from pydantic.alias_generators import to_camel
from caseconverter import snakecase


class AppBaseModel(SQLModel):
    @declared_attr
    def __tablename__(cls) -> str:
        return snakecase(cls.__name__)

    id: int | None = Field(default=None, primary_key=True)
    create_date: datetime = Field(default_factory=datetime.now)
    modify_date: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        protected_namespaces=(),
        from_attributes=True,
    )


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


class AppBaseTableModel(AppBaseModel):
    __table_args__ = {"schema": "testapi"}


class User(AppBaseTableModel, table=True):
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


class UserAddress(AppBaseTableModel, table=True):
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
        foreign_key=f"{AppBaseTableModel.__table_args__.get('schema')}.user.id",
        nullable=False,
    )
    user: User = Relationship(back_populates="inputs")
