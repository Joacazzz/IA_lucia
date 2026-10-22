from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioIn, UsuarioOut
from ..security import hash_password, require_admin

router = APIRouter(prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.ativo.is_(True)).order_by(Usuario.id).all()


@router.post("", status_code=201, response_model=UsuarioOut)
def criar(body: UsuarioIn, db: Session = Depends(get_db)):
    if db.query(Usuario.id).filter(Usuario.email == body.email).first():
        raise HTTPException(400, "E-mail já cadastrado.")
    u = Usuario(nome=body.nome, email=body.email, senha_hash=hash_password(body.senha), papel=body.papel)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
