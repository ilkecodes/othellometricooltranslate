from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "LGS Adaptive Platform"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "lgs_user"
    POSTGRES_PASSWORD: str = "lgs_pass"
    POSTGRES_DB: str = "lgs_db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
