# Refatoração do Sistema Lucía

## Por que estava pesado

| Causa | Efeito |
|---|---|
| Painel usava React **de desenvolvimento** + **Babel no navegador** (`<script type="text/babel">`) | ~3,7 MB de JS por carga e ~700 linhas de JSX compiladas no navegador a cada abertura |
| Dashboard baixava 200 protocolos inteiros e contava no navegador | Payload grande, cálculo repetido a cada render |
| Rotas `async def` chamando SQLAlchemy síncrono | Cada consulta travava o event loop (inclusive o WebSocket) |
| Sem índices em `status`/`criado_em`, sem paginação | Listagens e filtros crescendo com a tabela |
| Gráficos recriados a cada render (`key={JSON.stringify(...)}`) | Re-render pesado |

## O que mudou

**Backend (`app/`)** — dividido em módulos (config, models, schemas, security, routers, seed).
- Rotas de banco viram `def` (threadpool); broadcast do WebSocket via `BackgroundTasks`.
- `GET /protocolos` agora tem `limit`, `offset`, `q` (busca) e devolve o total no header `X-Total-Count` (o corpo continua sendo uma lista).
- Novo `GET /dashboard/resumo`: totais por status/departamento, últimos 7 dias e 5 recentes, agregados no banco, em 1 requisição.
- Índices novos (`criado_em`, `status+criado_em`), criados automaticamente no startup em bancos existentes.
- Pool de conexões configurado (`pool_pre_ping`), GZip nas respostas.
- Número do protocolo agora vem do `id` (antes `count()+1`, que **gerava número duplicado depois de excluir um protocolo** e dava erro 500).
- Datas saem em UTC com fuso (antes apareciam 3 h deslocadas no painel).
- WebSocket exige token: `/ws?token=...`.
- Status validado (`Aberto`, `Em andamento`, `Resolvido`, `Cancelado`).
- Dependências enxutas (removidos `requests`, `httpx`, `python-multipart`, `python-dotenv`, `python-jose` → `PyJWT`).
- Removidos: `users.py` (stub), `atendimento_lucia.py` e `config.py` antigo (não usados pela API).

**Painel (`frontend/`)** — Vite + React 18 em produção, Chart.js só com o que é usado e carregado sob demanda, busca/paginação no servidor, reconexão automática do WebSocket, logout automático quando o token expira, sem dados de demonstração.

## Medidas

- Antes: ~3,7 MB de JS (Babel 2,3 MB + react-dom dev 1,08 MB + Chart.js 205 KB + react 110 KB), mais a compilação no navegador.
- Depois: 164 KB iniciais (53 KB gzip) + 187 KB do dashboard (65 KB gzip) carregados sob demanda.
- Teste local com 60 protocolos: dashboard pronto ~0,9 s após o login.
- Testes: 11 testes de API passando no Python 3.14 (`pytest`) e um teste de navegador (login, dashboard, paginação, busca, criar protocolo, tempo real, mudar status, token inválido). Também validei o código novo contra uma cópia do seu `lucia.db` atual.
- **Não testado:** Postgres/Railway e o deploy no Vercel (só SQLite local).

## Segurança — fazer junto com o deploy

1. A `SECRET_KEY` antiga estava no código do repositório público: qualquer um conseguia forjar um token de admin. Agora ela vem do ambiente. Gere uma nova e **defina no Railway antes do deploy** (sem ela a API se recusa a subir, de propósito). Todos terão que fazer login de novo.
2. O admin tem a senha `admin123` (estava escrita na tela de login). Depois do deploy, troque em `/docs` → `POST /auth/trocar-senha`.
3. `lucia.db` estava versionado no Git (agora no `.gitignore`; rode `git rm --cached lucia.db`). O histórico do Git ainda contém a chave e o arquivo antigos.

## Deploy

1. Railway → Variables: `SECRET_KEY` (nova) e, se quiser, `CORS_ORIGINS=https://seu-painel.vercel.app`.
2. Substitua os arquivos do repositório por estes (apague `main.py`, `config.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`, `users.py`, `atendimento_lucia.py`, `painel_lucia_v2.html`, `procfile`, `requirements.txt` antigos). A API passa a iniciar com `uvicorn app.main:app`.
3. Vercel → Root Directory `frontend`, Framework Vite, variável `VITE_API_URL=https://ialucia-production.up.railway.app`.
4. Publique backend e painel juntos: o painel antigo não envia token no WebSocket e perderia o tempo real.

## Rodar local

O projeto usa Python 3.14 (definido em `.python-version`). No Windows, crie o ambiente virtual com essa versão:

```bash
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --reload
```

A API fica em http://localhost:8000/docs. Em outro terminal, inicie o painel:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

## Ainda recomendo (não mexi para não mudar comportamento)

- Qualquer usuário logado pode excluir protocolos e atendentes; talvez só admin.
- Sem limite de tentativas no login.
- Não aumente `--workers`: o WebSocket guarda conexões em memória do processo.
- Alembic para migrações, em vez de `create_all` + `CREATE INDEX IF NOT EXISTS`.
