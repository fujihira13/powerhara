from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",  # docker-composeが付与するPOSTGRES_PASSWORDなどの余分なキーを許容
    )
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/powerharafilter"
    POSTGRES_PASSWORD: str | None = None  # DBコンテナ用。アプリでは未使用だが環境変数として許容する。
    
    # JWT Settings
    SECRET_KEY: str = "dev-secret-key-not-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Settings
    DEBUG: bool = True


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()
