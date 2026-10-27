import os

os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "lucia_test"
os.environ["DATABASE_URL"] = ""
os.environ["SECRET_KEY"] = "teste-secret-key-com-tamanho-suficiente-123456"
os.environ["ADMIN_PASSWORD"] = "senha-de-teste-1"

import pytest
import mongomock
from fastapi.testclient import TestClient

from app import database

database.client = mongomock.MongoClient()
database.db = database.client["lucia_test"]

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
