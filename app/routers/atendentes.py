from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..documents import next_id
from ..schemas import AtendenteIn, AtendenteOut
from ..security import get_current_user

router = APIRouter(prefix="/atendentes", tags=["Atendentes"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[AtendenteOut])
def listar(departamento: Optional[str] = None, db=Depends(get_db)):
    filtro = {"ativo": True}
    if departamento:
        filtro["departamento_chave"] = departamento
    return list(db.atendentes.find(filtro).sort("nome", 1))


@router.post("", status_code=201, response_model=AtendenteOut)
def criar(body: AtendenteIn, db=Depends(get_db)):
    if db.atendentes.find_one({"email": body.email}, {"_id": 1}):
        raise HTTPException(400, "E-mail já cadastrado.")
    if not db.departamentos.find_one({"chave": body.departamento_chave}, {"_id": 1}):
        raise HTTPException(400, "Departamento inválido.")
    a = {
        "id": next_id("atendentes"),
        "nome": body.nome,
        "email": body.email,
        "departamento_chave": body.departamento_chave,
        "ativo": True,
    }
    db.atendentes.insert_one(a)
    return a


@router.delete("/{id}")
def desativar(id: int, db=Depends(get_db)):
    a = db.atendentes.find_one({"id": id})
    if not a:
        raise HTTPException(404, "Atendente não encontrado.")
    db.atendentes.update_one({"id": id}, {"$set": {"ativo": False}})
    return {"mensagem": f"Atendente {a['nome']} desativado."}
