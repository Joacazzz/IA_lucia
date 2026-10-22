"""Criação de tabelas, índices e dados iniciais (executado no startup)."""
import logging
import secrets

from sqlalchemy import text

from .config import settings
from .database import Base, SessionLocal, engine
from .models import Departamento, Usuario
from .security import hash_password

log = logging.getLogger("lucia")

# Índices novos para bancos já existentes (create_all não altera tabelas prontas).
# Os nomes são os mesmos declarados em models.py, então é seguro rodar sempre.
_INDEXES = (
    "CREATE INDEX IF NOT EXISTS ix_protocolos_criado_em ON protocolos (criado_em)",
    "CREATE INDEX IF NOT EXISTS ix_protocolos_status_criado ON protocolos (status, criado_em)",
    "CREATE INDEX IF NOT EXISTS ix_atendentes_departamento_chave ON atendentes (departamento_chave)",
)

DEPARTAMENTOS = [
    ("suporte",    "Suporte Tecnico",          "🛠️", "1001", "suporte@empresa.com.br",    "Seg-Sex 08h-18h", "Problemas tecnicos e sistemas."),
    ("rh",         "Recursos Humanos",         "👥", "1002", "rh@empresa.com.br",         "Seg-Sex 08h-17h", "Admissao, ferias e beneficios."),
    ("financeiro", "Financeiro",               "💰", "1003", "financeiro@empresa.com.br", "Seg-Sex 09h-17h", "Pagamentos e cobracas."),
    ("obras",      "Secretaria de Obras",      "🏗️", "1004", "obras@empresa.com.br",      "Seg-Sex 07h-16h", "Licencas e alvaras."),
    ("juridico",   "Juridico",                 "⚖️", "1005", "juridico@empresa.com.br",   "Seg-Sex 09h-18h", "Contratos e compliance."),
    ("ouvidoria",  "Ouvidoria",                "📢", "1006", "ouvidoria@empresa.com.br",  "Seg-Sex 08h-18h", "Reclamacoes e sugestoes."),
    ("compras",    "Compras e Licitacoes",     "🛒", "1007", "compras@empresa.com.br",    "Seg-Sex 08h-17h", "Fornecedores e cotacoes."),
    ("ti",         "Tecnologia da Informacao", "💻", "1008", "ti@empresa.com.br",        "Seg-Sex 08h-18h", "Infraestrutura digital."),
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_indexes()
    with SessionLocal() as db:
        _seed_departamentos(db)
        _seed_admin(db)


def _ensure_indexes() -> None:
    try:
        with engine.begin() as conn:
            for stmt in _INDEXES:
                conn.execute(text(stmt))
    except Exception:  # índice é otimização; nunca derruba a API
        log.exception("Não foi possível criar índices")


def _seed_departamentos(db) -> None:
    if db.query(Departamento.id).first():
        return
    db.add_all(
        Departamento(chave=c, nome=n, icone=i, ramal=r, email=e, horario=h, descricao=d)
        for c, n, i, r, e, h, d in DEPARTAMENTOS
    )
    db.commit()


def _seed_admin(db) -> None:
    if db.query(Usuario.id).first():
        return
    senha = settings.ADMIN_PASSWORD or secrets.token_urlsafe(12)
    db.add(Usuario(nome="Administrador", email=settings.ADMIN_EMAIL,
                   senha_hash=hash_password(senha), papel="admin"))
    db.commit()
    if settings.ADMIN_PASSWORD:
        log.warning("Admin inicial criado: %s", settings.ADMIN_EMAIL)
    else:
        log.warning("Admin inicial criado: %s | senha temporária: %s (troque em POST /auth/trocar-senha)",
                    settings.ADMIN_EMAIL, senha)
