from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db, Usuario

SECRET_KEY = "lucia-sistema-atendimento-2026"
ALGORITHM  = "HS256"
TOKEN_HORAS = 8

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(plain: str):
    return pwd_context.hash(plain.encode("utf-8")[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_HORAS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email: raise exc
    except JWTError:
        raise exc
    user = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()
    if not user: raise exc
    return user

def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.papel != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return current_user
