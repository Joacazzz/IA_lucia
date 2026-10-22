"""Configuração central. Tudo vem de variáveis de ambiente (ou .env em dev)."""
import logging
import secrets
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("lucia")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./lucia.db"
    SECRET_KEY: str = ""
    # "*" mantém o comportamento anterior. Em produção, prefira a URL do Vercel.
    CORS_ORIGINS: str = "*"
    TOKEN_HORAS: int = 8
    TIMEZONE: str = "America/Sao_Paulo"

    # Usados apenas na PRIMEIRA execução, quando ainda não existe nenhum usuário.
    ADMIN_EMAIL: str = "admin@lucia.com"
    ADMIN_PASSWORD: str = "123@mudar"

    @model_validator(mode="after")
    def _validar(self):
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        if not self.SECRET_KEY:
            if self.is_sqlite:
                # Dev local: chave aleatória por processo (tokens caem ao reiniciar).
                self.SECRET_KEY = secrets.token_urlsafe(48)
                log.warning("SECRET_KEY ausente: usando chave temporária (apenas dev).")
            else:
                raise ValueError(
                    "SECRET_KEY não definida. Gere uma com: "
                    "python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
        return self

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
