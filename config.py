from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GITHUB_TOKEN: str
    STATS_REFRESH_INTERVAL_HOURS: int = 1
    LEADERBOARD_CACHE_TTL: int = 900

    class Config:
        env_file = ".env"

settings = Settings()