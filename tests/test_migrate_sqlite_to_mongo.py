import sqlite3

import mongomock
import pytest

from app import migrate_sqlite_to_mongo as migrator


def test_migrate_importa_ids_datas_e_impede_repeticao(tmp_path, monkeypatch):
    source = tmp_path / "lucia.db"
    with sqlite3.connect(source) as sqlite_db:
        sqlite_db.execute(
            "CREATE TABLE usuarios (id INTEGER, nome TEXT, email TEXT, senha_hash TEXT, "
            "papel TEXT, ativo BOOLEAN, criado_em TEXT)"
        )
        sqlite_db.execute(
            "INSERT INTO usuarios VALUES (7, 'Admin', 'admin@example.com', 'hash', "
            "'admin', 1, '2026-01-02 12:30:00')"
        )
        sqlite_db.execute(
            "CREATE TABLE protocolos (id INTEGER, numero TEXT, departamento_chave TEXT, "
            "nome_solicitante TEXT, contato TEXT, descricao TEXT, status TEXT, "
            "criado_em TEXT, atualizado_em TEXT)"
        )
        sqlite_db.execute(
            "INSERT INTO protocolos VALUES (42, '20260102-0042', 'rh', 'Ana', '', "
            "'Teste', 'Aberto', '2026-01-02 12:30:00', '2026-01-02 12:30:00')"
        )

    target = mongomock.MongoClient().lucia
    monkeypatch.setattr(migrator, "db", target)

    migrator.migrate(source)

    assert target.usuarios.find_one({"id": 7})["email"] == "admin@example.com"
    protocolo = target.protocolos.find_one({"id": 42})
    assert protocolo["criado_em"].isoformat() == "2026-01-02T12:30:00"
    assert target.counters.find_one({"_id": "protocolos"})["value"] == 42
    with pytest.raises(RuntimeError, match="não está vazia"):
        migrator.migrate(source)
