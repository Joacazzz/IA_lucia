# Lucía — Sistema de Atendimento

Aplicação para registrar e acompanhar solicitações de atendimento. O projeto tem
uma API em FastAPI e um painel em React/Vite, com dashboard, protocolos,
atendentes, departamentos e notificações em tempo real.

## Requisitos

- Python 3.14
- Node.js e npm

A versão de Python do projeto está indicada em `.python-version`.

## Executar localmente no Windows

Abra um PowerShell na pasta do projeto. Se `py -3.14` não estiver disponível,
use `python` quando ele já apontar para Python 3.14.

### 1. Configurar o MongoDB Atlas

Crie um cluster no MongoDB Atlas, um usuário de banco de dados e configure o
acesso de rede para a API. Copie a connection string do Atlas para o arquivo
`.env` na raiz:

```dotenv
MONGODB_URI=mongodb+srv://<usuario>:<senha>@<cluster>/
MONGODB_DATABASE=lucia
SECRET_KEY=<chave-gerada>
```

Substitua os marcadores pelos dados do seu cluster e codifique caracteres
especiais da senha na URL. Remova a variável antiga `DATABASE_URL`, se ainda
existir no `.env`. Não compartilhe nem versione esse arquivo.
Gere `SECRET_KEY` com
`python -c "import secrets; print(secrets.token_urlsafe(48))"`.

### 2. Preparar e iniciar a API

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Se o ambiente virtual já estiver ativo, não é necessário criá-lo novamente.
Com a API em execução:

- Documentação interativa: <http://localhost:8000/docs>
- Verificação de saúde: <http://localhost:8000/health>

O primeiro início cria as coleções, índices e departamentos padrão. As
configurações `ADMIN_EMAIL` e `ADMIN_PASSWORD` são usadas somente se ainda não
houver usuário cadastrado.

### 3. Preparar e iniciar o painel

Em outro terminal PowerShell:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Abra o endereço indicado pelo Vite, normalmente <http://localhost:5173>.

Para apontar o painel para uma API diferente, crie ou ajuste `frontend\.env`:

```dotenv
VITE_API_URL=http://localhost:8000
```

Reinicie o Vite depois de alterar esse arquivo. A URL deve ser a origem da API,
sem `/` no final. O endereço usado pelo painel em produção deve ser configurado
separadamente.

## Configuração da API

As configurações podem vir de variáveis de ambiente ou de um arquivo `.env` na
raiz. As principais são:

| Variável | Uso |
|---|---|
| `MONGODB_URI` | Connection string do MongoDB Atlas. |
| `MONGODB_DATABASE` | Nome da base; por padrão, `lucia`. |
| `SECRET_KEY` | Chave de assinatura dos tokens. Obrigatória fora do MongoDB local. |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula. |
| `ADMIN_EMAIL` | E-mail usado para criar o primeiro usuário administrador. |
| `ADMIN_PASSWORD` | Senha usada para criar o primeiro usuário administrador. |
| `TOKEN_HORAS` | Duração dos tokens de autenticação, em horas. |
| `TIMEZONE` | Fuso horário dos dados do dashboard. |

Defina `ADMIN_EMAIL` e `ADMIN_PASSWORD` antes da primeira inicialização para
escolher as credenciais do administrador inicial. Não compartilhe nem versione
arquivos `.env` ou chaves secretas.

### Importar dados do antigo SQLite

Se já houver dados em `lucia.db`, faça a importação **antes de iniciar a API
com o novo banco**. O destino no Atlas precisa estar vazio; a ferramenta
interrompe a importação se encontrar dados para evitar duplicações.

Com `MONGODB_URI` e `MONGODB_DATABASE` configurados no `.env`, execute na raiz:

```powershell
python -m app.migrate_sqlite_to_mongo .\lucia.db
```

O importador mantém os IDs, protocolos, usuários e senhas existentes. Guarde
uma cópia de segurança do arquivo SQLite e confira a contagem exibida antes de
continuar.

## Testes e build

Na raiz do projeto, com o ambiente virtual ativado:

```powershell
python -m pytest -q
```

Para verificar o build de produção do painel:

```powershell
Set-Location .\frontend
npm run build
```

## Deploy

### API

O arquivo `render.yaml` prepara a API como Web Service no Render. Crie o serviço
a partir do repositório e informe as variáveis solicitadas:

- `MONGODB_URI`: connection string do Atlas.
- `MONGODB_DATABASE`: nome da base.
- `SECRET_KEY`: gere uma chave com
  `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `ADMIN_EMAIL` e `ADMIN_PASSWORD`: credenciais iniciais do administrador.
- `CORS_ORIGINS`: origem pública do painel, sem barra final.

No Atlas, crie um usuário de banco com permissões apenas na base da aplicação e
permita a conexão de rede do serviço do Render. Não use a chave secreta de
desenvolvimento em produção.

### Painel

Publique `frontend` como site estático (por exemplo, no Render) e defina
`VITE_API_URL` com a URL pública da API, sem `/` no final. Recompile/republique
o painel depois de alterar essa variável. A origem do painel deve constar em
`CORS_ORIGINS` na API para login, chamadas HTTP e WebSocket funcionarem.

## Interface

O painel usa um tema claro, com tons suaves de verde e azul-petróleo, layout
responsivo, gráficos de status e atividade recente. As páginas incluem visão
geral, protocolos, atendentes, departamentos e notificações em tempo real.

Para detalhes sobre as mudanças de desempenho e decisões da refatoração, veja
[REFATORACAO.md](./REFATORACAO.md).

##Licença
MIT
