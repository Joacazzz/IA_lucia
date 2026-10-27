from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..schemas import LoginIn, TrocarSenhaIn, UsuarioOut
from ..security import create_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# `def` (não `async def`): o bcrypt é CPU-bound e o acesso ao banco é síncrono;
# o FastAPI roda em threadpool e o event loop (WebSocket) continua livre.
@router.post("/login")
def login(body: LoginIn, db=Depends(get_db)):
    user = db.usuarios.find_one({"email": body.email, "ativo": True})
    if not user or not verify_password(body.password, user["senha_hash"]):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    return {
        "access_token": create_token(user["email"], user["papel"]),
        "token_type": "bearer",
        "user": UsuarioOut.model_validate(user),
    }


@router.get("/me", response_model=UsuarioOut)
def me(user: dict = Depends(get_current_user)):
    return user


@router.post("/trocar-senha")
def trocar_senha(body: TrocarSenhaIn, user: dict = Depends(get_current_user), db=Depends(get_db)):
    if not verify_password(body.senha_atual, user["senha_hash"]):
        raise HTTPException(400, "Senha atual incorreta.")
    db.usuarios.update_one({"id": user["id"]}, {"$set": {"senha_hash": hash_password(body.senha_nova)}})
    return {"mensagem": "Senha alterada."}
