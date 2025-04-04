import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlmodel import Session

from testapi import app_settings
from testapi.common.exceptions import UserDoesNotExistError
from testapi.common.models import User
from testapi.common.service import UserService
from testapi.database import get_session
from testapi.common.middleware import LogRoute
from testapi.common import schemas
from testapi.common.dependencies import CommonHeaders

router = APIRouter(
    tags=[
        "common",
    ],
    route_class=LogRoute,
)

logger = logging.getLogger(f"{app_settings.logger_name}.common")


@router.get("/healthcheck")
def get_healthcheck():
    logger.debug("Healthcheck")
    return {"msg": "Happy"}


@router.get("/info")
def get_info():
    return {
        k: v
        for k, v in app_settings.model_dump().items()
        if "password" not in k.lower()
    }


@router.post(
    path="/user",
    response_model=schemas.UserSchema,
    status_code=HTTPStatus.CREATED
)
def create_user(
    data: schemas.UserSchema,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user = user_service.create_user(user_data=data.model_dump())
    return user

@router.put(
    path="/user",
    response_model=schemas.UserSchema,
    status_code=HTTPStatus.OK
)
def update_user(
        data: schemas.UserSchema,
        headers: CommonHeaders = Depends(CommonHeaders),
        session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user = user_service.update_user(user_data=data.model_dump())
    return user

@router.get(
    path="/user/{username}",
    response_model=schemas.UserSchema,
    status_code=HTTPStatus.OK
)
def get_user(
        username: str,
        headers: CommonHeaders = Depends(CommonHeaders),
        session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user = user_service.get_user(username=username)
    if not user:
        raise UserDoesNotExistError(
            f"User with name {username} does not exist"
        )
    return user

@router.get(
    path="/user-all",
    response_model=list[schemas.UserSchema],
    status_code=HTTPStatus.OK
)
def get_user_all(
        search: str | None = None,
        headers: CommonHeaders = Depends(CommonHeaders),
        session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    results: list[User] = user_service.get_all_users(search=search)
    return results
