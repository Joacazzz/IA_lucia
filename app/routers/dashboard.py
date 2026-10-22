import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Protocolo
from ..schemas import DiaTotal, ResumoOut
from ..security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])
_TZ = ZoneInfo(settings.TIMEZONE)


@router.get("/resumo", response_model=ResumoOut)
def resumo(db: Session = Depends(get_db)):
    """Tudo que o dashboard precisa em UMA requisição, agregado no banco.

    Antes o painel baixava 200 protocolos completos e contava no navegador.
    """
    por_status = dict(db.query(Protocolo.status, func.count()).group_by(Protocolo.status).all())
    por_depto = dict(db.query(Protocolo.departamento_chave, func.count()).group_by(Protocolo.departamento_chave).all())

    hoje = dt.datetime.now(_TZ).date()
    dias = [hoje - dt.timedelta(days=i) for i in range(6, -1, -1)]
    inicio_utc = (
        dt.datetime.combine(dias[0], dt.time.min, tzinfo=_TZ).astimezone(dt.timezone.utc).replace(tzinfo=None)
    )
    contagem = dict.fromkeys(dias, 0)
    # Só a coluna de data, só da última semana (usa ix_protocolos_criado_em).
    for (criado,) in db.query(Protocolo.criado_em).filter(Protocolo.criado_em >= inicio_utc):
        local = criado.replace(tzinfo=dt.timezone.utc).astimezone(_TZ).date()
        if local in contagem:
            contagem[local] += 1

    recentes = db.query(Protocolo).order_by(Protocolo.criado_em.desc(), Protocolo.id.desc()).limit(5).all()

    return ResumoOut(
        total=sum(por_status.values()),
        por_status=por_status,
        por_departamento=por_depto,
        ultimos_7_dias=[DiaTotal(data=d.isoformat(), total=n) for d, n in contagem.items()],
        recentes=recentes,
    )
