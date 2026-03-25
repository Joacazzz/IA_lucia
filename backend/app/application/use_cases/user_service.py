from sqlalchemy.exc import IntegrityError

from app.application.dto.user_dto import UserCreateDTO, UserUpdateDTO
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class DuplicateEmailError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def list_users(self) -> list[User]:
        return self.repository.list_users()

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def create_user(self, payload: UserCreateDTO) -> User:
        try:
            return self.repository.create(name=payload.name, email=str(payload.email))
        except IntegrityError as exc:
            raise DuplicateEmailError from exc

    def update_user(self, user_id: int, payload: UserUpdateDTO) -> User | None:
        try:
            return self.repository.update(user_id=user_id, name=payload.name, email=str(payload.email) if payload.email else None)
        except IntegrityError as exc:
            raise DuplicateEmailError from exc

    def delete_user(self, user_id: int) -> bool:
        return self.repository.delete(user_id)
