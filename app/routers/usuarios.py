from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..documents import next_id, utcnow
from ..schemas import UsuarioIn, UsuarioOut
from ..security import hash_password, require_admin

router = APIRouter(prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UsuarioOut])
def listar(db=Depends(get_db)):
    return list(db.usuarios.find({"ativo": True}).sort("id", 1))


@router.post("", status_code=201, response_model=UsuarioOut)
def criar(body: UsuarioIn, db=Depends(get_db)):
    if db.usuarios.find_one({"email": body.email}, {"_id": 1}):
        raise HTTPException(400, "E-mail já cadastrado.")
    u = {
        "id": next_id("usuarios"),
        "nome": body.nome,
        "email": body.email,
        "senha_hash": hash_password(body.senha),
        "papel": body.papel,
        "ativo": True,
        "criado_em": utcnow(),
    }
    db.usuarios.insert_one(u)
    return u
