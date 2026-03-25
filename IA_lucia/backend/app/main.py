import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.users import router as users_router
from .config import settings
from .database import Base, engine


app = FastAPI(title="Users API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port)
