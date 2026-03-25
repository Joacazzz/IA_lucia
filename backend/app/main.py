from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.infrastructure.database.session import Base, engine
from app.infrastructure.persistence.sqlalchemy.models import UserModel  # noqa: F401
from app.presentation.api.v1.routes.users import router as users_router

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Lucía API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1")
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/health", tags=["Sistema"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", tags=["Sistema"])
def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
