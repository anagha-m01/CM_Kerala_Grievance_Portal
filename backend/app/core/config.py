from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    DATABASE_URL: str = 'sqlite:///./cm_kerala.db'
    JWT_SECRET: str = ''  # Required in .env: a random 32+ byte secret
    JWT_EXPIRE_MINUTES: int = 720
    CORS_ORIGINS: str = 'http://localhost:5173'
    GEMINI_API_KEY: str = ''
    GEMINI_MODEL: str = 'gemini-3.5-flash-lite'
    MAX_FILE_SIZE: int = 2 * 1024 * 1024
    DEMO_ADMIN_PASSWORD: str = ''
    DEMO_OFFICER_PASSWORD: str = ''
    DEMO_CITIZEN_PASSWORD: str = ''

    @property
    def database_uri(self) -> str:
        uri = self.DATABASE_URL
        if uri.startswith('postgres://'):
            return uri.replace('postgres://', 'postgresql+psycopg://', 1)
        if uri.startswith('postgresql://'):
            return uri.replace('postgresql://', 'postgresql+psycopg://', 1)
        return uri

    @property
    def origins(self) -> list[str]:
        return [s.strip() for s in self.CORS_ORIGINS.split(',') if s.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()