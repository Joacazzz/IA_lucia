import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends

from ..config import settings
from ..database import get_db
from ..schemas import DiaTotal, ResumoOut
from ..security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])
_TZ = ZoneInfo(settings.TIMEZONE)


@router.get("/resumo", response_model=ResumoOut)
def resumo(db=Depends(get_db)):
    """Retorna em uma requisição os totais necessários para o dashboard."""
    status_resultado = db.protocolos.aggregate([
        {"$group": {"_id": "$status", "total": {"$sum": 1}}},
    ])
    depto_resultado = db.protocolos.aggregate([
        {"$group": {"_id": "$departamento_chave", "total": {"$sum": 1}}},
    ])
    por_status = {item["_id"]: item["total"] for item in status_resultado}
    por_depto = {item["_id"]: item["total"] for item in depto_resultado}

    hoje = dt.datetime.now(_TZ).date()
    dias = [hoje - dt.timedelta(days=i) for i in range(6, -1, -1)]
    inicio_utc = (
        dt.datetime.combine(dias[0], dt.time.min, tzinfo=_TZ).astimezone(dt.timezone.utc).replace(tzinfo=None)
    )
    contagem = dict.fromkeys(dias, 0)
    for doc in db.protocolos.find({"criado_em": {"$gte": inicio_utc}}, {"criado_em": 1, "_id": 0}):
        criado = doc["criado_em"]
        local = criado.replace(tzinfo=dt.timezone.utc).astimezone(_TZ).date()
        if local in contagem:
            contagem[local] += 1

    recentes = list(db.protocolos.find().sort([("criado_em", -1), ("id", -1)]).limit(5))

    return ResumoOut(
        total=sum(por_status.values()),
        por_status=por_status,
        por_departamento=por_depto,
        ultimos_7_dias=[DiaTotal(data=d.isoformat(), total=n) for d, n in contagem.items()],
        recentes=recentes,
    )
