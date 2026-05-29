from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    REDIS_URL: str
    MAX_PDF_BYTES: int = 26214400
    PDF_TTL_SECONDS: int = 1800
    RESULT_TTL_SECONDS: int = 604800
    SF_INSTANCE_URL: str = ""
    SF_USERNAME: str = ""
    SF_PASSWORD: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
