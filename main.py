import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes.users import router as users_router
from .config import settings
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas ao iniciar
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Lucía API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Sistema"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    return {"sistema": "Lucía API", "status": "online", "docs": "/docs"}


app.include_router(users_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve o painel HTML na raiz
@app.get("/painel", tags=["Frontend"])
def painel():
    html_path = os.path.join(os.path.dirname(__file__), "painel_lucia_v2.html")
    return FileResponse(html_path)
