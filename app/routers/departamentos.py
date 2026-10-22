from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Departamento
from ..schemas import DepartamentoOut
from ..security import get_current_user

router = APIRouter(prefix="/departamentos", tags=["Departamentos"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[DepartamentoOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Departamento).filter(Departamento.ativo.is_(True)).order_by(Departamento.id).all()


@router.get("/{chave}", response_model=DepartamentoOut)
def buscar(chave: str, db: Session = Depends(get_db)):
    d = db.query(Departamento).filter(Departamento.chave == chave).first()
    if not d:
        raise HTTPException(404, "Departamento não encontrado.")
    return d
