from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application"""

    Adresse:str = "http://localhost:8000"


    # Base de données
    DATABASE_URL: str = "sqlite:///./bibliotheque.db"

    # Règles métier
    MAX_LOANS_PER_USER: int = 5
    LOAN_DURATION_DAYS: int = 14
    PENALTY_RATE_PER_DAY: float = 0.50
    MAX_PENALTY: float = 50.0

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"


settings = Settings()