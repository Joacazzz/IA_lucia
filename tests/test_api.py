import pytest
from starlette.websockets import WebSocketDisconnect


def novo(client, auth, nome="Ana", depto="rh", desc="Teste"):
    return client.post("/protocolos", headers=auth, json={
        "departamento_chave": depto, "nome_solicitante": nome, "contato": "x@y.com", "descricao": desc})


def test_login_e_rotas_protegidas(client, auth):
    assert client.get("/protocolos").status_code == 401
    assert client.get("/protocolos", headers={"Authorization": "Bearer lixo"}).status_code == 401
    assert client.post("/auth/login", json={"email": "admin@lucia.com", "password": "errada"}).status_code == 401
    assert client.get("/auth/me", headers=auth).json()["papel"] == "admin"


def test_departamentos_seed(client, auth):
    r = client.get("/departamentos", headers=auth)
    assert r.status_code == 200 and len(r.json()) == 8


def test_criar_protocolo_e_data_com_fuso(client, auth):
    r = novo(client, auth)
    assert r.status_code == 201
    p = r.json()
    assert p["numero"].endswith(f"-{p['id']:04d}")
    assert p["criado_em"].endswith("+00:00")  # navegador converte para horário local
    assert novo(client, auth, depto="inexistente").status_code == 400


def test_numero_nao_duplica_apos_exclusao(client, auth):
    a, b, c = (novo(client, auth, nome=f"N{i}").json() for i in range(3))
    assert client.delete(f"/protocolos/{b['numero']}", headers=auth).status_code == 200
    d = novo(client, auth, nome="depois").json()
    nums = {a["numero"], c["numero"], d["numero"]}
    assert len(nums) == 3  # com count()+1 o 4º colidia com um existente


def test_listagem_filtros_paginacao(client, auth):
    for i in range(5):
        novo(client, auth, nome=f"Zeca{i}", depto="ti")
    r = client.get("/protocolos", headers=auth, params={"q": "zeca", "limit": 2})
    assert len(r.json()) == 2
    assert int(r.headers["X-Total-Count"]) == 5
    r2 = client.get("/protocolos", headers=auth, params={"q": "zeca", "limit": 2, "offset": 4})
    assert len(r2.json()) == 1
    assert all(p["departamento_chave"] == "ti" for p in client.get("/protocolos?departamento=ti", headers=auth).json())
    assert client.get("/protocolos?limit=9999", headers=auth).status_code == 422


def test_patch_status(client, auth):
    p = novo(client, auth).json()
    r = client.patch(f"/protocolos/{p['numero']}", headers=auth, json={"status": "Resolvido"})
    assert r.status_code == 200 and r.json()["status"] == "Resolvido"
    assert client.patch(f"/protocolos/{p['numero']}", headers=auth, json={"status": "Qualquer"}).status_code == 422
    assert client.patch("/protocolos/nao-existe", headers=auth, json={"status": "Aberto"}).status_code == 404


def test_dashboard_resumo(client, auth):
    r = client.get("/dashboard/resumo", headers=auth)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == sum(d["por_status"].values()) > 0
    assert len(d["ultimos_7_dias"]) == 7
    assert sum(x["total"] for x in d["ultimos_7_dias"]) == d["total"]  # tudo foi criado hoje
    assert len(d["recentes"]) == 5


def test_atendentes(client, auth):
    r = client.post("/atendentes", headers=auth, json={"nome": "Maria", "email": "m@x.com", "departamento_chave": "rh"})
    assert r.status_code == 201
    assert client.post("/atendentes", headers=auth, json={"nome": "M2", "email": "m@x.com", "departamento_chave": "rh"}).status_code == 400
    assert client.delete(f"/atendentes/{r.json()['id']}", headers=auth).status_code == 200
    assert all(a["email"] != "m@x.com" for a in client.get("/atendentes", headers=auth).json())


def test_usuarios_so_admin_e_trocar_senha(client, auth):
    r = client.post("/usuarios", headers=auth, json={"nome": "Ate", "email": "ate@x.com", "senha": "12345678", "papel": "atendente"})
    assert r.status_code == 201
    tok = client.post("/auth/login", json={"email": "ate@x.com", "password": "12345678"}).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    assert client.get("/usuarios", headers=h).status_code == 403
    assert client.post("/auth/trocar-senha", headers=h, json={"senha_atual": "errada", "senha_nova": "novasenha1"}).status_code == 400
    assert client.post("/auth/trocar-senha", headers=h, json={"senha_atual": "12345678", "senha_nova": "novasenha1"}).status_code == 200
    assert client.post("/auth/login", json={"email": "ate@x.com", "password": "novasenha1"}).status_code == 200


def test_websocket_exige_token_e_recebe_broadcast(client, auth):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=invalido"):
            pass
    token = auth["Authorization"].split()[1]
    with client.websocket_connect(f"/ws?token={token}") as ws:
        p = novo(client, auth, nome="Realtime").json()
        msg = ws.receive_json()
        assert msg["tipo"] == "novo_protocolo" and msg["protocolo"] == p["numero"]


def test_secret_key_obrigatoria_fora_do_sqlite():
    from app.config import Settings
    with pytest.raises(ValueError):
        Settings(DATABASE_URL="postgresql://u:p@h/db", SECRET_KEY="")
