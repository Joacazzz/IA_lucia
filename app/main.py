import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .config import settings
from .realtime import manager
from .routers import atendentes, auth, dashboard, departamentos, protocolos, usuarios
from .security import decode_token
from .seed import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="API Sistema Lucía", version="2.1.0", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1024)  # listas JSON comprimem ~80%
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

for r in (auth, departamentos, protocolos, atendentes, usuarios, dashboard):
    app.include_router(r.router)


@app.get("/", tags=["Sistema"])
def raiz():
    return {"sistema": "Lucía", "status": "online", "docs": "/docs"}


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = ""):
    if not decode_token(token):
        await ws.close(code=4401)  # não autenticado
        return
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # mantém a conexão; o cliente envia "ping" periódico
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
