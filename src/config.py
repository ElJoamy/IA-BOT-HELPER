from enum import Enum
from functools import cache
from pydantic_settings import BaseSettings


class GPTModel(str, Enum):
    gpt_4 = "gpt-4"
    gpt_3_5_turbo = "gpt-3.5-turbo"

# class SentimentModel(str, Enum):
#     karina = "karina-aquino/spanish-sentiment-model"

class Settings(BaseSettings):
    service_name: str = "AssistBot API AI with Telegram TEST"
    k_revision: str = "local"
    log_level: str = "DEBUG"
    openai_key: str
    model: GPTModel = GPTModel.gpt_4
    telegram_token: str
    sentiment_model_id: str = "karina-aquino/spanish-sentiment-model"
    api_url: str = "http://localhost:8000/"
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    class Config:
        env_file = ".env"


@cache
def get_settings():
    return Settings()