from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """集中管理 API 配置，方便后续扩展。"""

    app_name: str = "MyriadStar API"
    environment: str = "local"
    api_prefix: str = "/api"

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
