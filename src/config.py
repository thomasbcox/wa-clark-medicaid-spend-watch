from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: str = str(DATA_DIR / "processed" / "medicaid_watch.db")
    
    # CMS / HHS Source (2026 Release)
    HHS_SOURCE_URL: str = "https://stopendataprod.blob.core.windows.net/datasets/medicaid-provider-spending/2026-02-09/medicaid-provider-spending.csv"
    
    # Analysis Scope
    TARGET_COUNTY: str = "CLARK"
    TARGET_STATE: str = "WA"
    
    # Anomaly Thresholds
    Z_SCORE_THRESHOLD: float = 5.0
    MIN_PEER_COUNT: int = 3
    SUDDEN_UTILIZATION_LIMIT: float = 1_000_000.0
    EXTREME_CONCENTRATION_THRESHOLD: float = 0.95
    MIN_CONCENTRATION_SPEND: float = 250_000.0
    VOLUME_OUTLIER_MULTIPLIER: float = 10.0
    MIN_VOLUME_CLAIMS: int = 500

    class Config:
        case_sensitive = True

settings = Settings()
