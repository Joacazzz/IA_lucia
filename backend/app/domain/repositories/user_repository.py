from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def list_users(self) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, name: str, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def update(self, user_id: int, name: str | None, email: str | None) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        raise NotImplementedError
