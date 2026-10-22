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

### 1. Preparar e iniciar a API

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

Por padrão, o backend usa SQLite no arquivo `lucia.db`. O banco e a senha de um
usuário já existente são preservados; a configuração de usuário inicial só é
usada quando ainda não há usuários cadastrados.

### 2. Preparar e iniciar o painel

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
| `DATABASE_URL` | Banco de dados. Sem configuração, usa `sqlite:///./lucia.db`. |
| `SECRET_KEY` | Chave de assinatura dos tokens. Em produção, é obrigatória. |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula. |
| `ADMIN_EMAIL` | E-mail usado para criar o primeiro usuário administrador. |
| `ADMIN_PASSWORD` | Senha usada para criar o primeiro usuário administrador. |
| `TOKEN_HORAS` | Duração dos tokens de autenticação, em horas. |
| `TIMEZONE` | Fuso horário dos dados do dashboard. |

Defina `ADMIN_EMAIL` e `ADMIN_PASSWORD` antes da primeira inicialização para
escolher as credenciais do administrador inicial. Não compartilhe nem versione
arquivos `.env` ou chaves secretas.

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

O comando de inicialização está em `railway.toml`. No Railway, configure ao
menos `SECRET_KEY` e `DATABASE_URL`; configure também `CORS_ORIGINS` com a
origem publicada do painel. Não use a chave de desenvolvimento em produção.

### Painel

Publique a pasta `frontend` como aplicação Vite e defina `VITE_API_URL` com a
URL pública da API, sem `/` no final. Recompile/republique o painel depois de
alterar essa variável. A API e o painel devem ser publicados juntos para que
login, chamadas HTTP e WebSocket usem a configuração correta.

## Interface

O painel usa um tema claro, com tons suaves de verde e azul-petróleo, layout
responsivo, gráficos de status e atividade recente. As páginas incluem visão
geral, protocolos, atendentes, departamentos e notificações em tempo real.

Para detalhes sobre as mudanças de desempenho e decisões da refatoração, veja
[REFATORACAO.md](./REFATORACAO.md).

##Licença
MIT
