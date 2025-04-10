from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


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


class AppStandardResponse(AppBaseSchema):
    message: str
