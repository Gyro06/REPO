from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    github_token: str = Field(alias="GITHUB_TOKEN")
    github_api_url: str = Field(default="https://api.github.com", alias="GITHUB_API_URL")
    github_allowed_org: str = Field(alias="GITHUB_ALLOWED_ORG")
    github_allowed_repos: str = Field(default="", alias="GITHUB_ALLOWED_REPOS")
    github_default_base_branch: str = Field(default="main", alias="GITHUB_DEFAULT_BASE_BRANCH")

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="github_dev_mcp", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="", alias="POSTGRES_PASSWORD")

    mcp_host: str = Field(default="127.0.0.1", alias="MCP_HOST")
    mcp_port: int = Field(default=8000, alias="MCP_PORT")

    @property
    def postgres_dsn(self) -> str:
        password_part = f":{self.postgres_password}" if self.postgres_password else ""
        return (
            f"postgresql://{self.postgres_user}{password_part}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def allowed_repos(self) -> set[str]:
        return {x.strip() for x in self.github_allowed_repos.split(",") if x.strip()}


settings = Settings()