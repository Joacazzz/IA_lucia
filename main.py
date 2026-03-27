from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import datetime
import os

from database import get_db, criar_banco, Departamento, Protocolo, Atendente, Usuario
from auth import hash_password, verify_password, create_token, get_current_user, require_admin
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(title="API Sistema Lucía v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket Manager ──────────────────────────────────────────
class WSManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, msg: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = WSManager()

# ── Startup ────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    criar_banco()
    _seed_deptos()
    _seed_admin()

def _seed_admin():
    from database import SessionLocal
    db = SessionLocal()
    if db.query(Usuario).count() == 0:
        db.add(Usuario(
            nome="Administrador",
            email="admin@lucia.com",
            senha_hash=hash_password("admin123"),
            papel="admin"
        ))
        db.commit()
    db.close()

def _seed_deptos():
    from database import SessionLocal
    db = SessionLocal()
    if db.query(Departamento).count() == 0:
        deptos = [
            Departamento(chave="suporte",    nome="Suporte Tecnico",          icone="🛠️",  ramal="1001", email="suporte@empresa.com.br",   horario="Seg-Sex 08h-18h", descricao="Problemas tecnicos e sistemas."),
            Departamento(chave="rh",         nome="Recursos Humanos",         icone="👥",  ramal="1002", email="rh@empresa.com.br",         horario="Seg-Sex 08h-17h", descricao="Admissao, ferias e beneficios."),
            Departamento(chave="financeiro", nome="Financeiro",               icone="💰",  ramal="1003", email="financeiro@empresa.com.br", horario="Seg-Sex 09h-17h", descricao="Pagamentos e cobracas."),
            Departamento(chave="obras",      nome="Secretaria de Obras",      icone="🏗️", ramal="1004", email="obras@empresa.com.br",      horario="Seg-Sex 07h-16h", descricao="Licencas e alvaras."),
            Departamento(chave="juridico",   nome="Juridico",                 icone="⚖️", ramal="1005", email="juridico@empresa.com.br",   horario="Seg-Sex 09h-18h", descricao="Contratos e compliance."),
            Departamento(chave="ouvidoria",  nome="Ouvidoria",                icone="📢",  ramal="1006", email="ouvidoria@empresa.com.br",  horario="Seg-Sex 08h-18h", descricao="Reclamacoes e sugestoes."),
            Departamento(chave="compras",    nome="Compras e Licitacoes",     icone="🛒",  ramal="1007", email="compras@empresa.com.br",    horario="Seg-Sex 08h-17h", descricao="Fornecedores e cotacoes."),
            Departamento(chave="ti",         nome="Tecnologia da Informacao", icone="💻",  ramal="1008", email="ti@empresa.com.br",         horario="Seg-Sex 08h-18h", descricao="Infraestrutura digital."),
        ]
        db.add_all(deptos)
        db.commit()
    db.close()

def _num(db):
    hoje  = datetime.datetime.now().strftime("%Y%m%d")
    total = db.query(Protocolo).count() + 1
    return f"{hoje}-{str(total).zfill(4)}"

# ── Schemas ────────────────────────────────────────────────────
class LoginIn(BaseModel):
    email: str
    password: str

class ProtoCreate(BaseModel):
    departamento_chave: str
    nome_solicitante: str
    contato: str
    descricao: str

class ProtoUpdate(BaseModel):
    status: Optional[str] = None
    descricao: Optional[str] = None

class AtendenteIn(BaseModel):
    nome: str
    email: str
    departamento_chave: str

class UsuarioIn(BaseModel):
    nome: str
    email: str
    senha: str
    papel: str = "atendente"

# ── Rotas Sistema ──────────────────────────────────────────────
@app.get("/", tags=["Sistema"])
def raiz():
    return {"sistema": "Lucía v2", "status": "online", "docs": "/docs"}

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}

# ── Auth ───────────────────────────────────────────────────────
@app.post("/auth/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(
        Usuario.email == form_data.username,
        Usuario.ativo == True
    ).first()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    token = create_token({"sub": user.email, "papel": user.papel})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "papel": user.papel
        }
    }
@app.get("/auth/me", tags=["Auth"])
def me(u: Usuario = Depends(get_current_user)):
    return {"id": u.id, "nome": u.nome, "email": u.email, "papel": u.papel}

# ── WebSocket ──────────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ── Departamentos ──────────────────────────────────────────────
@app.get("/departamentos", tags=["Departamentos"])
def listar_deptos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Departamento).filter(Departamento.ativo == True).all()

@app.get("/departamentos/{chave}", tags=["Departamentos"])
def buscar_depto(chave: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    d = db.query(Departamento).filter(Departamento.chave == chave).first()
    if not d:
        raise HTTPException(404, "Departamento não encontrado.")
    return d

# ── Protocolos ─────────────────────────────────────────────────
@app.get("/protocolos", tags=["Protocolos"])
def listar(
    departamento: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    q = db.query(Protocolo)
    if departamento: q = q.filter(Protocolo.departamento_chave == departamento)
    if status:       q = q.filter(Protocolo.status == status)
    return q.order_by(Protocolo.criado_em.desc()).limit(limit).all()

@app.get("/protocolos/{numero}", tags=["Protocolos"])
def buscar(numero: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p: raise HTTPException(404, "Protocolo não encontrado.")
    return p

@app.post("/protocolos", status_code=201, tags=["Protocolos"])
async def criar(body: ProtoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not db.query(Departamento).filter(Departamento.chave == body.departamento_chave).first():
        raise HTTPException(400, "Departamento inválido.")
    p = Protocolo(
        numero=_num(db),
        departamento_chave=body.departamento_chave,
        nome_solicitante=body.nome_solicitante,
        contato=body.contato,
        descricao=body.descricao,
        status="Aberto"
    )
    db.add(p); db.commit(); db.refresh(p)
    d = db.query(Departamento).filter(Departamento.chave == body.departamento_chave).first()
    await manager.broadcast({
        "tipo": "novo_protocolo",
        "mensagem": f"Novo protocolo {p.numero} — {d.nome if d else body.departamento_chave}",
        "protocolo": p.numero,
        "departamento": body.departamento_chave,
        "timestamp": datetime.datetime.now().isoformat()
    })
    return p

@app.patch("/protocolos/{numero}", tags=["Protocolos"])
async def atualizar(numero: str, body: ProtoUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p: raise HTTPException(404, "Protocolo não encontrado.")
    if body.status:    p.status    = body.status
    if body.descricao: p.descricao = body.descricao
    p.atualizado_em = datetime.datetime.utcnow()
    db.commit(); db.refresh(p)
    await manager.broadcast({
        "tipo": "status_atualizado",
        "mensagem": f"Protocolo {p.numero} → {p.status}",
        "protocolo": p.numero,
        "status": p.status,
        "timestamp": datetime.datetime.now().isoformat()
    })
    return p

@app.delete("/protocolos/{numero}", tags=["Protocolos"])
def deletar(numero: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Protocolo).filter(Protocolo.numero == numero).first()
    if not p: raise HTTPException(404, "Protocolo não encontrado.")
    db.delete(p); db.commit()
    return {"mensagem": f"Protocolo {numero} removido."}

# ── Atendentes ─────────────────────────────────────────────────
@app.get("/atendentes", tags=["Atendentes"])
def listar_atendentes(departamento: Optional[str] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Atendente).filter(Atendente.ativo == True)
    if departamento: q = q.filter(Atendente.departamento_chave == departamento)
    return q.all()

@app.post("/atendentes", status_code=201, tags=["Atendentes"])
def add_atendente(body: AtendenteIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(Atendente).filter(Atendente.email == body.email).first():
        raise HTTPException(400, "E-mail já cadastrado.")
    a = Atendente(nome=body.nome, email=body.email, departamento_chave=body.departamento_chave)
    db.add(a); db.commit(); db.refresh(a)
    return a

@app.delete("/atendentes/{id}", tags=["Atendentes"])
def del_atendente(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    a = db.query(Atendente).filter(Atendente.id == id).first()
    if not a: raise HTTPException(404, "Atendente não encontrado.")
    a.ativo = False; db.commit()
    return {"mensagem": f"Atendente {a.nome} desativado."}

# ── Usuários (admin) ───────────────────────────────────────────
@app.get("/usuarios", tags=["Usuários"])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(Usuario).filter(Usuario.ativo == True).all()
    return [{"id": u.id, "nome": u.nome, "email": u.email, "papel": u.papel} for u in users]

@app.post("/usuarios", status_code=201, tags=["Usuários"])
def criar_usuario(body: UsuarioIn, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Usuario).filter(Usuario.email == body.email).first():
        raise HTTPException(400, "E-mail já cadastrado.")
    u = Usuario(nome=body.nome, email=body.email,
                senha_hash=hash_password(body.senha), papel=body.papel)
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "nome": u.nome, "email": u.email, "papel": u.papel}

# ── Frontend ───────────────────────────────────────────────────
@app.get("/painel", tags=["Frontend"])
def painel_html():
    html_path = os.path.join(os.path.dirname(__file__), "painel_lucia_v2.html")
    return FileResponse(html_path)