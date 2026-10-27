import datetime as dt
import re
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response

from ..config import settings
from ..database import get_db
from ..documents import next_id, utcnow
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
    db=Depends(get_db),
):
    filtro = {}
    if departamento:
        filtro["departamento_chave"] = departamento
    if status:
        filtro["status"] = status
    if q:
        termo = re.escape(q.strip())
        filtro["$or"] = [
            {"nome_solicitante": {"$regex": termo, "$options": "i"}},
            {"numero": {"$regex": termo, "$options": "i"}},
        ]
    response.headers["X-Total-Count"] = str(db.protocolos.count_documents(filtro))
    return list(
        db.protocolos.find(filtro)
        .sort([("criado_em", -1), ("id", -1)])
        .skip(offset)
        .limit(limit)
    )


@router.get("/{numero}", response_model=ProtocoloOut)
def buscar(numero: str, db=Depends(get_db)):
    p = db.protocolos.find_one({"numero": numero})
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    return p


@router.post("", status_code=201, response_model=ProtocoloOut)
def criar(body: ProtoCreate, background: BackgroundTasks, db=Depends(get_db)):
    depto = db.departamentos.find_one({"chave": body.departamento_chave})
    if not depto:
        raise HTTPException(400, "Departamento inválido.")

    agora = utcnow()
    protocolo_id = next_id("protocolos")
    numero = f"{dt.datetime.now(_TZ):%Y%m%d}-{protocolo_id:04d}"
    p = {
        "id": protocolo_id,
        "numero": numero,
        "departamento_chave": body.departamento_chave,
        "nome_solicitante": body.nome_solicitante,
        "contato": body.contato,
        "descricao": body.descricao,
        "status": "Aberto",
        "criado_em": agora,
        "atualizado_em": agora,
    }
    db.protocolos.insert_one(p)

    background.add_task(manager.broadcast, {
        "tipo": "novo_protocolo",
        "mensagem": f"Novo protocolo {p['numero']} — {depto['nome']}",
        "protocolo": p["numero"],
        "departamento": p["departamento_chave"],
        "timestamp": _agora(),
    })
    return p


@router.patch("/{numero}", response_model=ProtocoloOut)
def atualizar(numero: str, body: ProtoUpdate, background: BackgroundTasks, db=Depends(get_db)):
    p = db.protocolos.find_one({"numero": numero})
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    atualizacao = {}
    if body.status:
        atualizacao["status"] = body.status
    if body.descricao:
        atualizacao["descricao"] = body.descricao
    if atualizacao:
        atualizacao["atualizado_em"] = utcnow()
        db.protocolos.update_one({"id": p["id"]}, {"$set": atualizacao})
        p.update(atualizacao)

    background.add_task(manager.broadcast, {
        "tipo": "status_atualizado",
        "mensagem": f"Protocolo {p['numero']} → {p['status']}",
        "protocolo": p["numero"],
        "status": p["status"],
        "timestamp": _agora(),
    })
    return p


@router.delete("/{numero}")
def deletar(numero: str, db=Depends(get_db)):
    p = db.protocolos.find_one({"numero": numero})
    if not p:
        raise HTTPException(404, "Protocolo não encontrado.")
    db.protocolos.delete_one({"id": p["id"]})
    return {"mensagem": f"Protocolo {numero} removido."}
