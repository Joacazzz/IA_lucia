from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users():
    return {"users": []}


@router.post("/")
def create_user():
    return {"message": "User created"}