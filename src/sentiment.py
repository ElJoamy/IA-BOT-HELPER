from transformers import pipeline
from src.config import get_settings

_SETTINGS = get_settings()


class SentimentAnalysisService:
    def __init__(self):
        self.sentiment_pipe = pipeline("text-classification", model=_SETTINGS.sentiment_model_id)

    def analyze_sentiment(self, text):
        return self.sentiment_pipe(text)