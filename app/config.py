from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    mongodb_uri: str = Field(default="mongodb://mongo:27017/t1db", alias="MONGODB_URI")
    app_env: str = Field(default="dev", alias="APP_ENV")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": False,
    }

settings = Settings()
