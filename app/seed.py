"""Criação de índices e dados iniciais (executado no startup)."""
import logging
import secrets

from .config import settings
from .database import client, db
from .documents import next_id, utcnow
from .security import hash_password

log = logging.getLogger("lucia")

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
    client.admin.command("ping")
    db.usuarios.create_index("email", unique=True)
    db.departamentos.create_index("chave", unique=True)
    db.protocolos.create_index("numero", unique=True)
    db.atendentes.create_index("email", unique=True)
    for collection in ("usuarios", "departamentos", "protocolos", "atendentes"):
        db[collection].create_index("id", unique=True)
    db.protocolos.create_index([("criado_em", -1), ("id", -1)])
    db.protocolos.create_index([("status", 1), ("criado_em", -1)])
    db.atendentes.create_index("departamento_chave")

    _seed_departamentos()
    _seed_admin()


def _seed_departamentos() -> None:
    if db.departamentos.find_one({}, {"_id": 1}):
        return
    documentos = [
        {
            "id": next_id("departamentos"),
            "chave": chave,
            "nome": nome,
            "icone": icone,
            "ramal": ramal,
            "email": email,
            "horario": horario,
            "descricao": descricao,
            "ativo": True,
        }
        for chave, nome, icone, ramal, email, horario, descricao in DEPARTAMENTOS
    ]
    db.departamentos.insert_many(documentos)


def _seed_admin() -> None:
    if db.usuarios.find_one({}, {"_id": 1}):
        return
    senha = settings.ADMIN_PASSWORD or secrets.token_urlsafe(12)
    db.usuarios.insert_one({
        "id": next_id("usuarios"),
        "nome": "Administrador",
        "email": settings.ADMIN_EMAIL,
        "senha_hash": hash_password(senha),
        "papel": "admin",
        "ativo": True,
        "criado_em": utcnow(),
    })
    if settings.ADMIN_PASSWORD:
        log.warning("Admin inicial criado: %s", settings.ADMIN_EMAIL)
    else:
        log.warning("Admin inicial criado: %s | senha temporária: %s (troque em POST /auth/trocar-senha)",
                    settings.ADMIN_EMAIL, senha)
