import datetime as dt
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Usuario

ALGORITHM = "HS256"

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
_bearer = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    return _pwd.hash(plain[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain[:72], hashed)


def create_token(email: str, papel: str) -> str:
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=settings.TOKEN_HORAS)
    return jwt.encode({"sub": email, "papel": papel, "exp": exp}, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


def _unauthorized() -> HTTPException:
    return HTTPException(401, "Token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if not credentials:
        raise _unauthorized()
    payload = decode_token(credentials.credentials)
    email = payload.get("sub") if payload else None
    if not email:
        raise _unauthorized()
    user = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo.is_(True)).first()
    if not user:
        raise _unauthorized()
    return user


def require_admin(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.papel != "admin":
        raise HTTPException(403, "Acesso restrito a administradores.")
    return user
