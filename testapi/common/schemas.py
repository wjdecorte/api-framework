from typing import Dict, List, Optional
import re

from pydantic import BaseModel, model_validator
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from testapi.common.models import UserStatus, AddressType


def extract_suite_info(address: str) -> str | None:
    # Case-insensitive pattern to match variations of "suite" followed by numbers/letters
    # This handles formats like:
    # - Suite 100
    # - suite #123
    # - Ste. 45A
    # - Ste 67-B
    # - Suite No. 789
    pattern = r'(suite|ste|suit|unit)[.\s#]*([a-zA-Z0-9][\w\s-]*\b)'

    # Search for the pattern in the address (case-insensitive)
    match = re.search(pattern, address, re.IGNORECASE)

    if match:
        suite_word = match.group(1)  # The matched "suite" variation
        suite_number = match.group(2).strip()  # The suite number/identifier
        return f"{suite_word} {suite_number}"

    return None

class ValidationErrorDetailSchema(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: str


class ValidationErrorSchema(BaseModel):
    errors: List[ValidationErrorDetailSchema]
    body: Optional[Dict]


class AppBaseSchema(BaseModel):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        protected_namespaces=(),
        from_attributes=True,
    )


class UserAddressSchema(AppBaseSchema):
    type: AddressType = AddressType.HOME
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str

    @model_validator(mode="after")
    @classmethod
    def post_serialization(cls, data):
        if data.address_line_2 is None:
            # check for suite in line 1
            suite = extract_suite_info(data.address_line_1)
            if suite is not None:
                data.address_line_2 = suite
                data.address_line_1 = data.address_line_1.replace(suite, "")
        return data


class UserSchema(AppBaseSchema):
    username: str
    description: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str
    addresses: List[UserAddressSchema]
    phone_number: str | None = None
    status: UserStatus = UserStatus.ACTIVE

