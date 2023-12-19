from pydantic import BaseModel
from typing import List, Dict, Union

class CombinedReportResponse(BaseModel):
    nombre_archivo: str
    label: str
    score: float
    fecha_hora: str
    tiempo_ejecucion: float
    modelos: str
    longitud_texto: int
    uso_memoria: int
    uso_cpu: float

class SentimentAnalysisResponse(BaseModel):
    prediction: Dict[str, Union[str, float]]  # 'label' es un string y 'score' un float
    execution_info: Dict[str, Union[float, str]]

class TextAnalysisResponse(BaseModel):
    nlp_analysis: Dict[str, Union[List[str], Dict[str, int]]]  # Ajusta según tus datos
    sentiment_analysis: Dict[str, Union[str, float]]  # 'label' es un string y 'score' un float
    execution_info: Dict[str, Union[float, str]]  # Incluye tipos float y str

class StatusResponse(BaseModel):
    service_name: str
    version: str
    log_level: str
    status: str
    models_info: Dict[str, str]

class SentimentRequest(BaseModel):
    text: str
    log_id: int

class AnalysisRequest(BaseModel):
    text: str
    log_id: int

class PersonalizedResponse(BaseModel):
    message: str

class PersonalizedRequest(BaseModel):
    text: str

class SuggestionRequest(BaseModel):
    message: str
    preference: str

class SuggestionResponse(BaseModel):
    recommendation: str