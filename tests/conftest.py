import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["SECRET_KEY"] = "teste-secret-key-com-tamanho-suficiente-123456"
os.environ["ADMIN_PASSWORD"] = "senha-de-teste-1"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth(client):
    r = client.post("/auth/login", json={"email": "admin@lucia.com", "password": "senha-de-teste-1"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
