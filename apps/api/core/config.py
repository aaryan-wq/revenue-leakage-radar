from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://rlr:rlr_dev_password@localhost:5432/revenue_leakage_radar"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 250
    cors_origins: str = "http://localhost:3000"
    clerk_secret_key: str = ""
    clerk_jwt_issuer: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    celery_task_always_eager: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
