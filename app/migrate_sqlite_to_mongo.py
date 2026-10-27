"""Importa registros do antigo banco SQLite para uma base MongoDB vazia."""
import argparse
import datetime as dt
import sqlite3
from pathlib import Path

from .database import db

_COLLECTIONS = {
    "usuarios": ("id", "nome", "email", "senha_hash", "papel", "ativo", "criado_em"),
    "departamentos": ("id", "chave", "nome", "icone", "ramal", "email", "horario", "descricao", "ativo"),
    "protocolos": (
        "id", "numero", "departamento_chave", "nome_solicitante", "contato",
        "descricao", "status", "criado_em", "atualizado_em",
    ),
    "atendentes": ("id", "nome", "email", "departamento_chave", "ativo"),
}
_DATE_FIELDS = {"criado_em", "atualizado_em"}


def _data(value):
    if isinstance(value, str):
        parsed = dt.datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            return parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)
        return parsed
    return value


def migrate(source: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Arquivo SQLite não encontrado: {source}")

    collections = [db[name] for name in (*_COLLECTIONS, "counters")]
    if any(collection.count_documents({}) for collection in collections):
        raise RuntimeError("A base MongoDB não está vazia; a importação foi cancelada.")

    for collection, fields in _COLLECTIONS.items():
        db[collection].create_index("id", unique=True)
    db.usuarios.create_index("email", unique=True)
    db.departamentos.create_index("chave", unique=True)
    db.protocolos.create_index("numero", unique=True)
    db.atendentes.create_index("email", unique=True)

    with sqlite3.connect(source) as sqlite_db:
        sqlite_db.row_factory = sqlite3.Row
        tables = {
            row[0]
            for row in sqlite_db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        found_tables = tables.intersection(_COLLECTIONS)
        if not found_tables:
            raise RuntimeError("O arquivo não contém tabelas reconhecidas da Lucía.")

        for collection, fields in _COLLECTIONS.items():
            if collection not in tables:
                continue
            columns = {row[1] for row in sqlite_db.execute(f"PRAGMA table_info({collection})")}
            selected = [field for field in fields if field in columns]
            if "id" not in selected:
                raise RuntimeError(f"A tabela {collection} não possui a coluna id.")
            documents = []
            for row in sqlite_db.execute(f"SELECT {', '.join(selected)} FROM {collection}"):
                document = dict(row)
                for field in _DATE_FIELDS.intersection(document):
                    document[field] = _data(document[field])
                documents.append(document)
            if documents:
                db[collection].insert_many(documents)
                max_id = max(document["id"] for document in documents)
                db.counters.insert_one({"_id": collection, "value": max_id})
            print(f"{collection}: {len(documents)} registro(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sqlite_file", type=Path, help="Caminho para lucia.db")
    args = parser.parse_args()
    migrate(args.sqlite_file)


if __name__ == "__main__":
    main()
