from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"

    def get_origins(self):
        return self.CORS_ORIGINS.split(",")


settings = Settings()