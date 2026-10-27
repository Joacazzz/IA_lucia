"""Configuração central. Tudo vem de variáveis de ambiente (ou .env em dev)."""
import logging
import secrets
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("lucia")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = ""
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "lucia"
    SECRET_KEY: str = ""
    CORS_ORIGINS: str = "*"
    TOKEN_HORAS: int = 8
    TIMEZONE: str = "America/Sao_Paulo"

    # Usados apenas na primeira execução, quando ainda não existe nenhum usuário.
    ADMIN_EMAIL: str = "admin@lucia.com"
    ADMIN_PASSWORD: str = "123@mudar"

    @model_validator(mode="after")
    def _validar(self):
        if self.DATABASE_URL:
            raise ValueError("DATABASE_URL não é mais suportada; remova-a e configure MONGODB_URI.")
        if not self.MONGODB_URI.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URI deve ser uma connection string MongoDB.")
        if not self.MONGODB_DATABASE.strip():
            raise ValueError("MONGODB_DATABASE não pode estar vazia.")
        if not self.SECRET_KEY:
            if self.is_local_mongodb:
                self.SECRET_KEY = secrets.token_urlsafe(48)
                log.warning("SECRET_KEY ausente: usando chave temporária (apenas desenvolvimento local).")
            else:
                raise ValueError(
                    "SECRET_KEY não definida. Gere uma com: "
                    "python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
        return self

    @property
    def is_local_mongodb(self) -> bool:
        return urlparse(self.MONGODB_URI).hostname in {"localhost", "127.0.0.1"}

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
