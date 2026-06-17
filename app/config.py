import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "AQ.Ab8RN6KmJk8WBBJcCorRhcGK8ms0fF9bw5hKgBQBUn_8X-KoLQ-gemini api key"
    DB_PATH: str = "bevinsight.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
