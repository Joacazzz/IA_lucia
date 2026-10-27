from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..schemas import DepartamentoOut
from ..security import get_current_user

router = APIRouter(prefix="/departamentos", tags=["Departamentos"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[DepartamentoOut])
def listar(db=Depends(get_db)):
    return list(db.departamentos.find({"ativo": True}).sort("id", 1))


@router.get("/{chave}", response_model=DepartamentoOut)
def buscar(chave: str, db=Depends(get_db)):
    d = db.departamentos.find_one({"chave": chave})
    if not d:
        raise HTTPException(404, "Departamento não encontrado.")
    return d
