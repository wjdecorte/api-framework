from sqlmodel import Session, select

from api_framework.common import logger
from api_framework.user.exceptions import UserAlreadyExistError, UserDoesNotExistError
from api_framework.user.models import User, UserAddress


class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user(
        self, search: str = None, username: str = None
    ) -> list[User] | User:
        statement = select(User)
        if search:
            statement = statement.where(User.username.ilike(f"%{search}%")).order_by(
                User.username
            )
        elif username:
            statement = statement.where(User.username == username)
        statement = statement.order_by(User.username)
        results = self.session.exec(statement)
        if username:
            return results.first()
        else:
            return list(results.all())

    async def get_address_by_type(self, address_type: int) -> UserAddress:
        statement = select(UserAddress).where(UserAddress.type == address_type)
        address = self.session.exec(statement).first()  # noqa
        return address

    async def create_user(self, user_data: dict) -> User:
        username = user_data.get("username")
        logger.info("Creating user %s", username)
        user = await self.get_user(username=username)
        logger.debug(f"{user=}")
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

    async def update_user(self, user_data: dict):
        username = user_data.get("username")
        user = await self.get_user(username=username)
        if not user:
            raise UserDoesNotExistError(
                message=f"User with name {username} doesn't exist"
            )
        user_addresses = user_data.pop("addresses")
        user.sqlmodel_update(user_data)

        updated_addresses = []
        for address in user_addresses:
            existing_address = await self.get_address_by_type(address.get("type"))
            if existing_address:
                existing_address.sqlmodel_update(address)
                updated_addresses.append(existing_address)
            else:
                updated_addresses.append(UserAddress(**address))

        user.addresses = updated_addresses
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    async def delete_user(self, username: str) -> User:
        if not (user := await self.get_user(username=username)):
            raise UserDoesNotExistError
        self.session.delete(user)
        self.session.commit()
        return user

    def save_user(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()
