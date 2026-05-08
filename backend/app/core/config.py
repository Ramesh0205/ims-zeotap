from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://mongo:27017"
    POSTGRES_URL: str = "postgresql+asyncpg://ims:ims123@postgres:5432/ims_db"
    REDIS_URL: str = "redis://redis:6379"
    DEBOUNCE_WINDOW: int = 10
    DEBOUNCE_THRESHOLD: int = 100
    RATE_LIMIT_PER_SECOND: int = 500
    class Config:
        env_file = ".env"

settings = Settings()
