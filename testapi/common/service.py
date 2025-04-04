from sqlmodel import Session, select

from testapi.common.exceptions import UserAlreadyExistError, UserDoesNotExistError
from testapi.common.models import (
    User,
    UserAddress,
)
from testapi.common import logger


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_all_users(self, search: str = None) -> list[User]:
        if search:
            statement = (
                select(User)
                .where(User.username.ilike(f"%{search}%"))  # noqa
                .order_by(User.username)
            )
        else:
            statement = select(User).order_by(User.username)
        results = self.session.exec(statement).all()
        logger.info(f"{len(results)=}")
        return list(results)

    def get_user(self, username: str) -> User:
        statement = select(User).where(User.username == username)
        user = self.session.exec(statement).first()  # noqa
        return user

    def create_user(self, user_data: dict) -> User:
        username = user_data.get("username")
        logger.info("Creating user %s", username)
        user = self.get_user(username=username)
        if user:
            raise UserAlreadyExistError(
                message=f"User with name {username} already exists"
            )

        user_addresses = user_data.pop("addresses")
        user = User(**user_data)

        user.addresses = [
            UserAddress(
                **address_data,
                user_id=user.id,
            )
            for address_data in user_addresses
        ]

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user(self, user_data: dict):
        username = user_data.get("username")
        user = self.get_user(username=username)
        if not user:
            raise UserDoesNotExistError(
                message=f"User with name {username} doesn't exist"
            )

        user.description = user_data.get("description")
        user.email = user_data.get("email")
        user.first_name = user_data.get("first_name")
        user.last_name = user_data.get("last_name")
        user.phone_number = user_data.get("phone_number")
        user.status = user_data.get("status")

        user.addresses = [
            UserAddress(
                **address_data,
                user_id=user.id,
            )
            for address_data in user_data["addresses"]
        ]
        self.session.commit()
        return user

    def delete_user(self, username: str) -> User:
        if not (user := self.get_user(username=username)):
            raise UserDoesNotExistError
        self.session.delete(user)
        self.session.commit()
        return user

    def save_user(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()
