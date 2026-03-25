from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.sqlalchemy.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_entity(self, model: UserModel) -> User:
        return User(id=model.id, name=model.name, email=model.email)

    def list_users(self) -> list[User]:
        users = self.db.query(UserModel).order_by(UserModel.id.asc()).all()
        return [self._to_entity(user) for user in users]

    def get_by_id(self, user_id: int) -> User | None:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(user) if user else None

    def create(self, name: str, email: str) -> User:
        user = UserModel(name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._to_entity(user)

    def update(self, user_id: int, name: str | None, email: str | None) -> User | None:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            return None

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email

        self.db.commit()
        self.db.refresh(user)
        return self._to_entity(user)

    def delete(self, user_id: int) -> bool:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
