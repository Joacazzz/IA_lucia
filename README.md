# Lucía — Painel Administrativo (GitHub Pages)

Projeto simplificado para **deploy estático no GitHub Pages**.

## O que ficou no repositório

- `index.html`: painel administrativo estático (React via CDN + Chart.js via CDN).
- `.github/workflows/deploy-pages.yml`: workflow de deploy automático para GitHub Pages.

## O que foi removido

Para atender ao pedido de “remover tudo que não utiliza” com foco em GitHub Pages, foram removidos:

- backend FastAPI,
- estrutura de Clean Architecture,
- testes Python,
- arquivos e dependências de build Python.

## Deploy no GitHub Pages

### 1) Habilitar Pages no repositório

No GitHub:

1. **Settings** → **Pages**
2. Em **Build and deployment**, escolha **GitHub Actions**.

### 2) Push na branch principal

Ao fazer push em `main` ou `master`, o workflow `Deploy GitHub Pages` publica automaticamente o `index.html`.

### 3) URL publicada

Após o deploy, a URL será exibida no job e também em:

- **Settings** → **Pages**

## Configuração de API

O painel usa por padrão:

- `https://ialucia-production.up.railway.app`
- `wss://ialucia-production.up.railway.app/ws`

Se quiser sobrescrever em runtime, defina antes do app carregar:

```html
<script>
  window.API = "https://sua-api.com";
  window.WS_URL = "wss://sua-api.com/ws";
</script>
```

## Desenvolvimento local

Basta abrir `index.html` no navegador.
