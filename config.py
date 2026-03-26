import os


class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = "HS256"

    def get_origins(self):
        return ["*"]


settings = Settings()