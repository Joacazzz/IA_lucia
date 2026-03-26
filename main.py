from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
import datetime
from database import get_db, criar_banco, Departamento, Protocolo, Atendente

app = FastAPI(title="API Sistema Lucia", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    criar_banco()
    _popular_departamentos()

class ProtocoloCreate(BaseModel):
    departamento_chave: str
    nome_solicitante: str
    contato: str
    descricao: str

class ProtocoloUpdate(BaseModel):
    status: Optional[str] = None
    descricao: Optional[str] = None

class AtendenteCreate(BaseModel):
    nome: str
    email: str
    departamento_chave: str

def _gerar_numero_protocolo(db):
    hoje = datetime.datetime.now().strftime("%Y%m%d")
    total = db.query(Protocolo).count() + 1
    return f"{hoje}-{str(total).zfill(4)}"

def _popular_departamentos():
    from database import SessionLocal
    db = SessionLocal()
    if db.query(Departamento).count() == 0:
        deptos = [
            Departamento(chave="suporte",    nome="Suporte Tecnico",          icone="S", ramal="1001", email="suporte@empresa.com.br",   horario="Seg-Sex 08h-18h", descricao="Problemas tecnicos e sistemas."),
            Departamento(chave="rh",         nome="Recursos Humanos",         icone="R", ramal="1002", email="rh@empresa.com.br",         horario="Seg-Sex 08h-17h", descricao="Admissao, ferias e beneficios."),
            Departamento(chave="financeiro", nome="Financeiro",               icone="F", ramal="1003", email="financeiro@empresa.com.br", horario="Seg-Sex 09h-17h", descricao="Pagamentos e cobracas."),
            Departamento(chave="obras",      nome="Secretaria de Obras",      icone="O", ramal="1004", email="obras@empresa.com.br",      horario="Seg-Sex 07h-16h", descricao="Licencas e alvaras."),
            Departamento(chave="juridico",   nome="Juridico",                 icone="J", ramal="1005", email="juridico@empresa.com.br",   horario="Seg-Sex 09h-18h", descricao="Contratos e compliance."),
            Departamento(chave="ouvidoria",  nome="Ouvidoria",                icone="V", ramal="1006", email="ouvidoria@empresa.com.br",  horario="Seg-Sex 08h-18h", descricao="Reclamacoes e sugestoes."),
            Departamento(chave="compras",    nome="Compras e Licitacoes",     icone="C", ramal="1007", email="compras@empresa.com.br",    horario="Seg-Sex 08h-17h", descricao="Fornecedores e cotacoes."),
            Departamento(chave="ti",         nome="Tecnologia da Informacao", icone="T", ramal="1008", email="ti@empresa.com.br",         horario="Seg-Sex 08h-18h", descricao="Infraestrutura digital."),
        ]
        db.add_all(deptos)
        db.commit()
    db.close()

@app.get("/")
def raiz():
    return {"sistema": "Lucia", "status": "online", "docs": "/docs"}

@app.get("/departamentos")
def listar_departamentos(db: Session = Depends(get_db)):
    return db.query(Departamento).filter(Departamento.ativo == True).all()

@app.get("/departamentos/{chave}")
def buscar_departamento(chave: str, db: Session = Depends(get_db)):
    d = db.query(Departamento).filter(Departamento.chave == chave).first()
    if not d:
        raise HTTPException(status_code=404, detail="Departamento nao encontrado.")
    return d

@app.get("/protocolos")
def listar_protocolos(departamento: Optional[str] = None, status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Protocolo)
    if departamento:
        q = q.filter(Protocolo.departamento_chave == departamento)
    if status:
        q = q.filter(Protocolo.status == status)
    return q.order_by(Protocolo.criado_em.desc()).limit(limit).all()

@app.get("/protocolos/{numero}")
def buscar_protocolo(numero: str, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo nao encontrado.")
    return p

@app.post("/protocolos", status_code=201)
def criar_protocolo(dados: ProtocoloCreate, db: Session = Depends(get_db)):
    if not db.query(Departamento).filter(Departamento.chave == dados.departamento_chave).first():
        raise HTTPException(status_code=400, detail="Departamento invalido.")
    p = Protocolo(numero=_gerar_numero_protocolo(db), departamento_chave=dados.departamento_chave,
                  nome_solicitante=dados.nome_solicitante, contato=dados.contato, descricao=dados.descricao, status="Aberto")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.patch("/protocolos/{numero}")
def atualizar_protocolo(numero: str, dados: ProtocoloUpdate, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo nao encontrado.")
    if dados.status:
        p.status = dados.status
    if dados.descricao:
        p.descricao = dados.descricao
    p.atualizado_em = datetime.datetime.utcnow()
    db.commit()
    db.refresh(p)
    return p

@app.delete("/protocolos/{numero}")
def deletar_protocolo(numero: str, db: Session = Depends(get_db)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo nao encontrado.")
    db.delete(p)
    db.commit()
    return {"mensagem": f"Protocolo {numero} removido."}

@app.get("/atendentes")
def listar_atendentes(departamento: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Atendente).filter(Atendente.ativo == True)
    if departamento:
        q = q.filter(Atendente.departamento_chave == departamento)
    return q.all()

@app.post("/atendentes", status_code=201)
def cadastrar_atendente(dados: AtendenteCreate, db: Session = Depends(get_db)):
    if db.query(Atendente).filter(Atendente.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email ja cadastrado.")
    a = Atendente(nome=dados.nome, email=dados.email, departamento_chave=dados.departamento_chave)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

@app.delete("/atendentes/{id}")
def remover_atendente(id: int, db: Session = Depends(get_db)):
    a = db.query(Atendente).filter(Atendente.id == id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Atendente nao encontrado.")
    a.ativo = False
    db.commit()
    return {"mensagem": f"Atendente {a.nome} desativado."}
