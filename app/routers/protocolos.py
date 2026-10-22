import datetime as dt
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Departamento, Protocolo
from ..realtime import manager
from ..schemas import ProtoCreate, ProtocoloOut, ProtoUpdate, Status
from ..security import get_current_user, require_admin

router = APIRouter(prefix="/protocolos", tags=["Protocolos"], dependencies=[Depends(get_current_user)])
_TZ = ZoneInfo(settings.TIMEZONE)


def _agora() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


@router.get("", response_model=list[ProtocoloOut])
def listar(
    response: Response,
    departamento: Optional[str] = None,
    status: Optional[Status] = None,
    q: Optional[str] = Query(None, max_length=100, description="Busca por nome do solicitante ou número"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Protocolo)
    if departamento:
        query = query.filter(Protocolo.departamento_chave == departamento)
    if status:
        query = query.filter(Protocolo.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(Protocolo.nome_solicitante.ilike(like) | Protocolo.numero.ilike(like))
    # Total (para paginação) vai no header: o corpo continua sendo uma lista simples.
    response.headers["X-Total-Count"] = str(query.count())
    return query.order_by(Protocolo.criado_em.desc(), Protocolo.id.desc()).offset(offset).limit(limit).all()


@router.get("/{numero}", response_model=ProtocoloOut)
def buscar(numero: str, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    return p


@router.post("", status_code=201, response_model=ProtocoloOut)
def criar(body: ProtoCreate, background: BackgroundTasks, db: Session = Depends(get_db)):
    depto = db.query(Departamento).filter(Departamento.chave == body.departamento_chave).first()
    if not depto:
        raise HTTPException(400, "Departamento inválido.")

    p = Protocolo(
        departamento_chave=body.departamento_chave,
        nome_solicitante=body.nome_solicitante,
        contato=body.contato,
        descricao=body.descricao,
        status="Aberto",
    )
    db.add(p)
    db.flush()  # gera o id sem depender de count()+1 (que gerava duplicata após exclusões)
    p.numero = f"{dt.datetime.now(_TZ):%Y%m%d}-{p.id:04d}"
    db.commit()
    db.refresh(p)

    background.add_task(manager.broadcast, {
        "tipo": "novo_protocolo",
        "mensagem": f"Novo protocolo {p.numero} — {depto.nome}",
        "protocolo": p.numero,
        "departamento": p.departamento_chave,
        "timestamp": _agora(),
    })
    return p


@router.patch("/{numero}", response_model=ProtocoloOut)
def atualizar(numero: str, body: ProtoUpdate, background: BackgroundTasks, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    if body.status:
        p.status = body.status
    if body.descricao:
        p.descricao = body.descricao
    db.commit()
    db.refresh(p)

    background.add_task(manager.broadcast, {
        "tipo": "status_atualizado",
        "mensagem": f"Protocolo {p.numero} → {p.status}",
        "protocolo": p.numero,
        "status": p.status,
        "timestamp": _agora(),
    })
    return p


@router.delete("/{numero}")
def deletar(numero: str, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    db.delete(p)
    db.commit()
    return {"mensagem": f"Protocolo {numero} removido."}
