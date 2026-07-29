import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SureBet Arbitrage System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-surebet-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./surebet.db")

    # Encryption key for sensitive odds or config (AES style or symmetric encryption key)
    # Generate a dummy base64 32-byte key for Fernet or simple cryptography
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "yP-4bV_R6fWbWb5mS_v7mD_t6L4pZp_B6jK7XGfR6u0=")

    # App Settings
    SCRAPING_INTERVAL_SECONDS: int = 60
    DEFAULT_INVESTMENT: float = 1000.0

    # Enabled Bookmakers
    BOOKMAKERS: list[str] = [
        "Bet365",
        "Betano",
        "Betfair",
        "Pinnacle",
        "1xBet",
        "Sportingbet"
    ]

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
