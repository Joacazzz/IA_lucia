import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text

from .database import Base


def utcnow() -> dt.datetime:
    """UTC 'naive' — mesmo formato que já está gravado no banco."""
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    papel = Column(String, default="atendente")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=utcnow)


class Departamento(Base):
    __tablename__ = "departamentos"
    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String, unique=True, index=True)
    nome = Column(String)
    icone = Column(String)
    ramal = Column(String)
    email = Column(String)
    horario = Column(String)
    descricao = Column(String)
    ativo = Column(Boolean, default=True)


class Protocolo(Base):
    __tablename__ = "protocolos"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    departamento_chave = Column(String, index=True)
    nome_solicitante = Column(String)
    contato = Column(String)
    descricao = Column(Text)
    status = Column(String, default="Aberto")
    criado_em = Column(DateTime, default=utcnow)
    atualizado_em = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("ix_protocolos_criado_em", "criado_em"),
        Index("ix_protocolos_status_criado", "status", "criado_em"),
    )


class Atendente(Base):
    __tablename__ = "atendentes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    departamento_chave = Column(String, index=True)
    ativo = Column(Boolean, default=True)
