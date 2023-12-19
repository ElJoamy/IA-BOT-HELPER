import os
import time
import requests
import openai
import spacy
import json
import psutil
from fastapi import FastAPI, UploadFile, File, HTTPException, status,Depends, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from functools import cache
from datetime import datetime
from starlette.middleware.cors import CORSMiddleware
from src.db.db_manage import DatabaseManager
from src.sentiment import SentimentAnalysisService
from src.config import get_settings
from typing import List
from src.response_models import (
    CombinedReportResponse,
    SentimentAnalysisResponse,
    TextAnalysisResponse,
    StatusResponse,
    SentimentRequest,
    AnalysisRequest,
    PersonalizedResponse,
    PersonalizedRequest,
    SuggestionRequest,
    SuggestionResponse
)


_SETTINGS = get_settings()

app = FastAPI(
    title=_SETTINGS.service_name,
    version=_SETTINGS.k_revision
)

db_manager = DatabaseManager(_SETTINGS.db_host, _SETTINGS.db_port, _SETTINGS.db_user, _SETTINGS.db_pass, _SETTINGS.db_name)

nlp = spacy.load("es_core_news_sm")

client = openai.OpenAI(api_key=_SETTINGS.openai_key)

def get_sentiment_service():
    return SentimentAnalysisService()

@app.get("/status", response_model=StatusResponse, summary="Obtiene estado del servicio", description="Obtiene el estado actual del servicio, incluyendo información sobre los modelos utilizados.")
def get_status():
    status = db_manager.get_status()
    if not status:
        status_data = {
            "service_name": _SETTINGS.service_name,
            "version": _SETTINGS.k_revision,
            "log_level": _SETTINGS.log_level,
            "status": "Running",
            "models_info": json.dumps({
                "sentiment_model": _SETTINGS.sentiment_model_id,
                "nlp_model": "Spacy es_core_news_sm",
                "gpt_model": _SETTINGS.model 
            })
        }
        db_manager.insert_status(status_data)
        status = db_manager.get_status()

    return {
        "service_name": status['service_name'],
        "version": status['version'],
        "log_level": status['log_level'],
        "status": status['status'],
        "models_info": json.loads(status['models_info'])
    }

@app.post("/sentiment", response_model=SentimentAnalysisResponse, summary="Analiza sentimiento", description="Realiza un análisis de sentimiento en el texto proporcionado.")
def analyze_sentiment(request: SentimentRequest, sentiment_service: SentimentAnalysisService = Depends(SentimentAnalysisService)):
    start_time = time.time()
    result = sentiment_service.analyze_sentiment(request.text)
    end_time = time.time()
    execution_time = end_time - start_time

    prediction_datetime = datetime.now().isoformat()
    text_length = len(request.text)
    model_version = _SETTINGS.sentiment_model_id
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info().rss
    cpu_usage = process.cpu_percent(interval=1)

    adjusted_score = (result[0]['score'] * 2) - 1

    db_data = (
        request.log_id,
        request.text,
        result[0]['label'],
        adjusted_score,
        prediction_datetime,
        execution_time,
        model_version,
        text_length,
        memory_info,
        cpu_usage
    )

    db_manager.insert_sentiment(*db_data)

    return {
        "prediction": {
            "label": result[0]['label'],  # Asegúrate de que 'label' sea un string
            "score": adjusted_score  # 'score' debe ser un float
        },
        "execution_info": {
            "execution_time": execution_time,  # float
            "prediction_datetime": prediction_datetime,  # string
            "text_length": text_length,  # int
            "model_version": model_version,  # string
            "memory_usage": memory_info,  # int
            "cpu_usage": cpu_usage  # float
        }
    }

@app.post("/personalized_response", response_model=PersonalizedResponse)
async def get_personalized_response(request: PersonalizedRequest):
    sentiment_label = analyze_sentiment(request.text)
    response_message = await generate_response_based_on_sentiment(sentiment_label, request.text)
    return {"message": response_message}


def analyze_sentiment(text):
    sentiment_service = get_sentiment_service()
    result = sentiment_service.analyze_sentiment(text)
    return result[0]['label']

# Modifica la función generate_response_based_on_sentiment para aceptar el log_id
async def generate_response_based_on_sentiment(sentiment_label, user_text):
    if sentiment_label in ['4', '5']:
        mood = "feliz"
    elif sentiment_label == '3':
        mood = "neutral"
    else:
        mood = "triste o enojado"

    prompt = f"Me siento {mood}. ¿Puedes proporcionar un mensaje de apoyo?"

    # Llama a la función para generar una respuesta basada en el sentimiento
    response = generate_response_with_gpt4(prompt, user_text)  # Pasa el texto del usuario y log_id
    return response

# Modifica la función generate_response_with_gpt4 para aceptar el log_id
def generate_response_with_gpt4(prompt, user_text):
    response = client.chat.completions.create(
        model=_SETTINGS.model,  # Utiliza GPT-4 para generar respuestas
        messages=[
            {"role": "system", "content": "Genera una respuesta basada en el sentimiento del usuario y responde siempre en español, ademas dale proverbios y refranes o algun chiste de acuerdo a su emocion, al final siempre recomiendale una cancion de acuerdo a su emocion, recuerda dar la respuesta en JSON"},
            {"role": "user", "content": user_text},  # Agrega el texto del usuario como entrada
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,  # Temperatura moderada
    )

    return response.choices[0].message.content

@app.post("/sugerencia", response_model=SuggestionResponse)
async def get_suggestion(request: SuggestionRequest):
    sentiment_service = SentimentAnalysisService()
    sentiment_result = sentiment_service.analyze_sentiment(request.message)
    sentiment_label = sentiment_result[0]['label']
    
    # Mapea la preferencia a un prompt específico para GPT-4
    prompts = {
        'libro': "Recomienda un libro para alguien que se siente {sentiment} y explica por qué lo recomiendas.",
        'video de youtube': "Recomienda un video de YouTube para alguien que se siente {sentiment} y explica por qué lo recomiendas.",
        'cancion': "Recomienda una canción para alguien que se siente {sentiment} y explica por qué la recomiendas",
        'serie': "Recomienda una serie para alguien que se siente {sentiment} y explica por qué la recomiendas y en que plataforma se puede ver.",
        'chiste': "Dime un chiste para alguien que se siente {sentiment}, trata de que tu chiste no sea muy basico o muy malo, usa tu poder para navegar en internet y encontrar un buen chiste.",
        'refran': "Comparte un refrán para alguien que se siente {sentiment} "
    }

    prompt = prompts[request.preference].format(sentiment=sentiment_label)
    
    # Hacer la llamada a OpenAI GPT-4 con el prompt correspondiente
    response = client.chat.completions.create(
        model=_SETTINGS.model,
        messages=[
            {"role": "system", "content": "El siguiente es un consejo para alguien basado en su estado de ánimo."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7  # Puede ajustar esto según sea necesario
    )

    recommendation = response.choices[0].message.content
    
    return SuggestionResponse(recommendation=recommendation)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", reload=True)