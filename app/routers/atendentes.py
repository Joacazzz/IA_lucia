from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Atendente, Departamento
from ..schemas import AtendenteIn, AtendenteOut
from ..security import get_current_user

router = APIRouter(prefix="/atendentes", tags=["Atendentes"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[AtendenteOut])
def listar(departamento: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Atendente).filter(Atendente.ativo.is_(True))
    if departamento:
        q = q.filter(Atendente.departamento_chave == departamento)
    return q.order_by(Atendente.nome).all()


@router.post("", status_code=201, response_model=AtendenteOut)
def criar(body: AtendenteIn, db: Session = Depends(get_db)):
    if db.query(Atendente.id).filter(Atendente.email == body.email).first():
        raise HTTPException(400, "E-mail já cadastrado.")
    if not db.query(Departamento.id).filter(Departamento.chave == body.departamento_chave).first():
        raise HTTPException(400, "Departamento inválido.")
    a = Atendente(nome=body.nome, email=body.email, departamento_chave=body.departamento_chave)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{id}")
def desativar(id: int, db: Session = Depends(get_db)):
    a = db.get(Atendente, id)
    if not a:
        raise HTTPException(404, "Atendente não encontrado.")
    a.ativo = False
    db.commit()
    return {"mensagem": f"Atendente {a.nome} desativado."}
