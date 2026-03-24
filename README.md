

# 🎯 Lucia – Sistema de Gestão de Protocolos

**Lucia** é uma aplicação backend moderna desenvolvida em **FastAPI**, projetada para gerenciamento de protocolos e atendimento de solicitações em múltiplos departamentos. É uma solução escalável, segura e pronta para produção, ideal para empresas ou órgãos públicos.

---

## 🏗️ Estrutura do Projeto

```
IA_lucia/
├─ main.py            # Ponto de entrada da aplicação FastAPI
├─ lucia.py           # Lógica principal da aplicação
├─ database.py        # Configuração e modelos do banco de dados
├─ painel_lucia.html   # Interface visual (frontend leve)
├─ requirements.txt   # Dependências do Python
├─ Procfile           # Comando para deploy em Railway/Heroku
├─ src/               # Código modular adicional
└─ README.md          # Documentação do projeto
```

---

## ⚡ Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI** – API backend moderna e rápida
* **SQLAlchemy** – ORM para PostgreSQL/SQLite
* **Uvicorn** – Servidor ASGI
* **WebSocket** – Notificações em tempo real
* **JWT + bcrypt** – Autenticação segura
* **CORS** – Suporte a frontends externos

---

## 🧩 Componentes Principais

### 1. Backend (FastAPI)

* Endpoints REST completos
* Autenticação JWT e roles de usuário (`admin`, `atendente`)
* WebSocket para notificações instantâneas
* CRUD completo de protocolos e atendentes

### 2. Banco de Dados

* **Usuários:** login, senha criptografada e permissões
* **Departamentos:** 8 departamentos pré-configurados

  * Suporte, RH, Financeiro, Obras, Jurídico, Ouvidoria, Compras, TI
* **Protocolos:** controle de solicitações, status e histórico
* **Atendentes:** gestão de staff por departamento

### 3. Funcionalidades Chave

* Criação automática de números de protocolo (`YYYYMMDD-####`)
* 4 status de protocolo: Aberto, Em andamento, Resolvido, Cancelado
* Filtragem por departamento e status
* Notificações em tempo real via WebSocket
* Suporte a PostgreSQL e SQLite
* CORS habilitado para frontend

### 4. Frontend

* Painel visual simples (`painel_lucia.html`) para interação básica

---

## 🚀 Deploy e Produção

* **Procfile** configurado para Railway ou Heroku:

```text
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

* Repositório pronto para deploy automático
* Arquitetura modular e limpa para manutenção futura

---

## ⚙️ Como Rodar Localmente

1. Criar e ativar ambiente virtual:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/macOS
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Rodar a aplicação:

```bash
uvicorn main:app --reload
```

4. Acessar no navegador:

```
http://127.0.0.1:8000
```

---

## ✅ Por que usar Lucia?

* Sistema completo **enterprise-grade** para gerenciamento de protocolos
* Fácil de adaptar e escalar
* Histórico e rastreamento completo de solicitações
* Notificações em tempo real para usuários e atendentes

---


