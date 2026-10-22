import datetime as dt
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

Status = Literal["Aberto", "Em andamento", "Resolvido", "Cancelado"]


def _utc_iso(v: Optional[dt.datetime]) -> Optional[str]:
    # O banco guarda UTC sem fuso. Sem o offset o navegador interpreta como horário
    # local e mostra a data com 3 h de diferença.
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=dt.timezone.utc)
    return v.isoformat()


UtcDateTime = Annotated[dt.datetime, PlainSerializer(_utc_iso, return_type=Optional[str])]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Auth ──
class LoginIn(BaseModel):
    email: str
    password: str


class TrocarSenhaIn(BaseModel):
    senha_atual: str
    senha_nova: str = Field(min_length=8, max_length=72)


class UsuarioOut(ORM):
    id: int
    nome: str
    email: str
    papel: str


class UsuarioIn(BaseModel):
    nome: str
    email: str
    senha: str = Field(min_length=8, max_length=72)
    papel: Literal["admin", "atendente"] = "atendente"


# ── Departamentos ──
class DepartamentoOut(ORM):
    id: int
    chave: str
    nome: str
    icone: Optional[str] = None
    ramal: Optional[str] = None
    email: Optional[str] = None
    horario: Optional[str] = None
    descricao: Optional[str] = None
    ativo: bool


# ── Protocolos ──
class ProtoCreate(BaseModel):
    departamento_chave: str
    nome_solicitante: str = Field(min_length=1, max_length=200)
    contato: str = Field(default="", max_length=200)
    descricao: str = Field(min_length=1, max_length=10_000)


class ProtoUpdate(BaseModel):
    status: Optional[Status] = None
    descricao: Optional[str] = Field(default=None, max_length=10_000)


class ProtocoloOut(ORM):
    id: int
    numero: str
    departamento_chave: str
    nome_solicitante: str
    contato: Optional[str] = None
    descricao: Optional[str] = None
    status: str
    criado_em: UtcDateTime
    atualizado_em: UtcDateTime


# ── Atendentes ──
class AtendenteIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    email: str
    departamento_chave: str


class AtendenteOut(ORM):
    id: int
    nome: str
    email: str
    departamento_chave: Optional[str] = None
    ativo: bool


# ── Dashboard ──
class DiaTotal(BaseModel):
    data: str  # YYYY-MM-DD, no fuso configurado
    total: int


class ResumoOut(BaseModel):
    total: int
    por_status: dict[str, int]
    por_departamento: dict[str, int]
    ultimos_7_dias: list[DiaTotal]
    recentes: list[ProtocoloOut]
