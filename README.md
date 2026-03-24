# IA Lucía - Sistema Completo (Clean Architecture)

Projeto fullstack dividido em:

- **Backend:** Node.js + Express + PostgreSQL com Clean Architecture.
- **Frontend:** React + Node.js + TailwindCSS com separação por camadas.

## 1) Arquitetura (Clean Architecture)

### Domain
Camada mais interna, com regras de negócio puras:
- Entidades (`Ticket`)
- Value Objects (`TicketStatus`)
- Contratos de repositório (`TicketRepository`)

### Application
Orquestra os casos de uso do sistema:
- `ListTicketsUseCase`
- `CreateTicketUseCase`
- `UpdateTicketStatusUseCase`

### Infrastructure
Implementações técnicas e integrações externas:
- Conexão PostgreSQL (`pg Pool`)
- Repositório concreto (`PostgresTicketRepository`)

### Presentation
Entrada e saída da aplicação:
- Backend: rotas e controllers HTTP (Express)
- Frontend: páginas, componentes React e hooks

---

## 2) Estrutura de Pastas

```text
.
├── apps/
│   ├── backend/
│   │   ├── migrations/
│   │   ├── src/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   └── presentation/
│   │   └── tests/
│   └── frontend/
│       ├── src/
│       │   ├── domain/
│       │   ├── application/
│       │   ├── infrastructure/
│       │   └── presentation/
│       ├── tailwind.config.js
│       └── postcss.config.js
├── packages/
│   └── shared/
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## 3) Melhorias Aplicadas

- Separação real entre camadas (backend e frontend).
- Regras de negócio desacopladas de frameworks.
- Uso de interfaces/contratos para inversão de dependência.
- Organização monorepo com workspaces.
- Setup para escalabilidade com package compartilhado (`packages/shared`).

---

## 4) Tecnologias

- Node.js
- Express
- PostgreSQL
- React
- TailwindCSS
- Docker (para banco local)
- GitHub Actions (CI/CD)

---

## 5) Setup de Ambiente

### Backend (`apps/backend/.env`)
Use como base `apps/backend/.env.example`:

```env
PORT=3333
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=lucia_db
```

### Frontend (`apps/frontend/.env`)
Use como base `apps/frontend/.env.example`:

```env
VITE_API_URL=http://localhost:3333/api
```

---

## 6) Como rodar localmente

### 1. Subir PostgreSQL

```bash
docker compose up -d
```

### 2. Instalar dependências do monorepo

```bash
npm install
```

### 3. Criar tabela no banco

Execute o SQL em `apps/backend/migrations/001_create_tickets.sql`.

### 4. Rodar backend

```bash
npm run dev:backend
```

### 5. Rodar frontend

```bash
npm run dev:frontend
```

---

## 7) Build

```bash
npm run build
```

Build do frontend em `apps/frontend/dist`.

---

## 8) CI/CD - GitHub Actions

Arquivo: `.github/workflows/ci.yml`

Pipeline com boas práticas:
- Trigger em `push` e `pull_request`
- Cache de dependências npm
- Job de testes backend
- Job de build frontend
- Upload de artefato (`frontend-dist`)
- Serviço PostgreSQL no job de backend

---

## 9) Endpoints principais (backend)

Base URL: `http://localhost:3333/api`

- `GET /tickets`
- `POST /tickets`
- `PATCH /tickets/:id/status`

Exemplo body `POST /tickets`:

```json
{
  "requesterName": "Maria",
  "department": "SUPORTE",
  "description": "Erro ao acessar o sistema"
}
```
