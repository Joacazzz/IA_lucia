from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.dto.user_dto import UserCreateDTO, UserUpdateDTO
from app.application.use_cases.user_service import DuplicateEmailError, UserService
from app.infrastructure.database.session import get_db_session
from app.infrastructure.persistence.sqlalchemy.user_repository import SQLAlchemyUserRepository
from app.presentation.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(SQLAlchemyUserRepository(db))


@router.get("", response_model=list[UserResponse])
def list_users(service: UserService = Depends(get_user_service)):
    return service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
def retrieve_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, service: UserService = Depends(get_user_service)):
    try:
        return service.create_user(UserCreateDTO(**payload.model_dump()))
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists") from exc


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdateRequest, service: UserService = Depends(get_user_service)):
    try:
        user = service.update_user(user_id=user_id, payload=UserUpdateDTO(**payload.model_dump()))
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists") from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
