from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lucia.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id         = Column(Integer, primary_key=True, index=True)
    nome       = Column(String)
    email      = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    papel      = Column(String, default="atendente")
    ativo      = Column(Boolean, default=True)
    criado_em  = Column(DateTime, default=datetime.datetime.utcnow)

class Departamento(Base):
    __tablename__ = "departamentos"
    id        = Column(Integer, primary_key=True, index=True)
    chave     = Column(String, unique=True, index=True)
    nome      = Column(String)
    icone     = Column(String)
    ramal     = Column(String)
    email     = Column(String)
    horario   = Column(String)
    descricao = Column(String)
    ativo     = Column(Boolean, default=True)

class Protocolo(Base):
    __tablename__ = "protocolos"
    id                 = Column(Integer, primary_key=True, index=True)
    numero             = Column(String, unique=True, index=True)
    departamento_chave = Column(String, index=True)
    nome_solicitante   = Column(String)
    contato            = Column(String)
    descricao          = Column(Text)
    status             = Column(String, default="Aberto")
    criado_em          = Column(DateTime, default=datetime.datetime.utcnow)
    atualizado_em      = Column(DateTime, default=datetime.datetime.utcnow,
                                onupdate=datetime.datetime.utcnow)

class Atendente(Base):
    __tablename__ = "atendentes"
    id                 = Column(Integer, primary_key=True, index=True)
    nome               = Column(String)
    email              = Column(String, unique=True)
    departamento_chave = Column(String)
    ativo              = Column(Boolean, default=True)

def criar_banco():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
