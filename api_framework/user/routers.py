import logging

from fastapi import Depends, APIRouter, status, Response
from sqlmodel import Session

from api_framework import app_settings
from api_framework.common.middleware import LogRoute
from api_framework.user.schemas import UserSchema
from api_framework.common.dependencies import CommonHeaders, get_session
from api_framework.user.exceptions import UserDoesNotExistError
from api_framework.user.services import UserService
from api_framework.user.models import User
from api_framework.common.routers import get_healthcheck


router = APIRouter(
    tags=[
        "user",
    ],
    route_class=LogRoute,
)

logger = logging.getLogger(f"{app_settings.logger_name}.user")

router.add_api_route(
    path="/healthcheck",
    endpoint=get_healthcheck,
    methods=["GET"],
)


@router.post(
    path="/create", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    data: UserSchema,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user = await user_service.create_user(user_data=data.model_dump())
    return user


@router.put(path="/update", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(
    data: UserSchema,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user = await user_service.update_user(user_data=data.model_dump(exclude_unset=True))
    return user


@router.get(
    path="/{username}", response_model=UserSchema, status_code=status.HTTP_200_OK
)
async def get_user(
    username: str,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    user: User = await user_service.get_user(username=username)
    if not user:
        raise UserDoesNotExistError(f"User with name {username} does not exist")
    return user


@router.get(path="/", response_model=list[UserSchema], status_code=status.HTTP_200_OK)
async def get_user_all(
    search: str | None = None,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    results: list[User] = await user_service.get_user(search=search)
    return results


@router.delete(
    path="/delete/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_user(
    username: str,
    headers: CommonHeaders = Depends(CommonHeaders),
    session: Session = Depends(get_session),
):
    user_service: UserService = UserService(session=session)
    _ = await user_service.delete_user(username=username)
