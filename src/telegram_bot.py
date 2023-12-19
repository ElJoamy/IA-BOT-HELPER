import asyncio
import telebot 
import requests
from telebot import types
from datetime import datetime
from src.config import get_settings
from src.db.db_manage import DatabaseManager

_SETTINGS = get_settings()

API_TOKEN =_SETTINGS.telegram_token

db_manager = DatabaseManager(_SETTINGS.db_host, _SETTINGS.db_port, _SETTINGS.db_user, _SETTINGS.db_pass, _SETTINGS.db_name)
print (API_TOKEN)

bot = telebot.TeleBot(API_TOKEN)

API_URL = get_settings().api_url

def log_user_data(user_id, user_name, command_time, comando):
    data = (user_id, user_name, command_time, command_time.date(), comando)
    return db_manager.insert_user_log(data)  # Devuelve log_id

def get_user_ids_from_log():
    try:
        user_ids = db_manager.get_user_ids()
        return user_ids
    except Exception as e:
        print(f"Error al obtener los user_ids de la base de datos: {e}")
        return set()

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    bot.reply_to(message, f"Hola {user_name}, bienvenido a tu virtual AI assistant que te ayudará a mejorar tu estado de ánimo y a encontrar recomendaciones personalizadas para ti, puedes ver los comandos disponibles con /help.")
    print(f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")

@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    help_message = (
        f"Hola {user_name}, aquí tienes ayuda sobre cómo utilizar el bot:\n\n"
        "Comandos disponibles:\n"
        "/start - Inicia la interacción con el bot y te da la bienvenida.\n"
        "/help - Muestra esta ayuda.\n"
        "/status - Obtiene el estado actual del servicio.\n"
        "/sentiment - Inicia el proceso para analizar el sentimiento de un texto.\n"
        "/amigo - Inicia el proceso para generar un mensaje personalizado basado en tu estado de ánimo.\n"
        "/sugerencia - Inicia el proceso para obtener una sugerencia basada en tu estado de ánimo.\n\n"
        "Si necesitas más información o asistencia, no dudes en escribir el comando correspondiente."
    )

    bot.reply_to(message, help_message)
    print(f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")


@bot.message_handler(commands=['status'])
def handle_status(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    allowed_user_ids = get_user_ids_from_log()
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "No tienes permiso para usar este comando.")
        return

    log_user_data(user_id, user_name, command_time, comando)

    status_url = API_URL + "status" 
    try:
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            reply_message = f"Nombre del servicio: {status_data['service_name']}\n" \
                            f"Versión: {status_data['version']}\n" \
                            f"Nivel de log: {status_data['log_level']}\n" \
                            f"Modelos utilizados:\n" \
                            f"  - Sentiment Model: {status_data['models_info']['sentiment_model']}\n" \
                            f"  - NLP Model: {status_data['models_info']['nlp_model']}\n" \
                            f"  - GPT Model: {status_data['models_info']['gpt_model']}"
        else:
            reply_message = "Error al obtener el estado del servicio."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    print(f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")
    bot.reply_to(message, reply_message)

@bot.message_handler(commands=['sentiment'])
def handle_sentiment(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_id = log_user_data(user_id, user_name, command_time, comando)

    bot.send_message(user_id, "Por favor, envía el texto para el análisis de sentimiento.")
    bot.register_next_step_handler(message, analyze_sentiment_step, log_id)


def analyze_sentiment_step(message, log_id):
    user_id = message.from_user.id
    text = message.text

    sentiment_url = API_URL + "sentiment"
    payload = {"text": text, "log_id": log_id}

    try:
        response = requests.post(sentiment_url, json=payload)
        if response.status_code == 200:
            sentiment_data = response.json()
            reply_message = construct_sentiment_reply(sentiment_data, text)
        else:
            reply_message = "Error al realizar el análisis de sentimiento."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    bot.send_message(user_id, reply_message)

def construct_sentiment_reply(sentiment_data, text):
    label = sentiment_data["prediction"]["label"]
    score = sentiment_data["prediction"]["score"]
    return f"Análisis de Sentimiento:\nTexto: {text}\nSentimiento: {label}\nPuntuación: {score}"

@bot.message_handler(commands=['amigo'])
def handle_amigo(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text

    log_user_data(user_id, user_name, command_time, comando)

    bot.send_message(user_id, "Por favor, envía un texto para generar un mensaje basado en tu estado de ánimo.")
    bot.register_next_step_handler(message, generate_personalized_response)

def generate_personalized_response(message):
    user_id = message.from_user.id
    text = message.text

    API_URL = _SETTINGS.api_url
    response_url = API_URL + "personalized_response"
    payload = {"text": text}

    try:
        response = requests.post(response_url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            reply_message = response_data["message"]
        else:
            reply_message = "Error al generar la respuesta personalizada."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"

    bot.send_message(user_id, reply_message)

@bot.message_handler(commands=['sugerencia'])
def handle_suggestion(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('libro', 'video de youtube', 'cancion', 'serie', 'chiste', 'refran')
    msg = bot.send_message(message.chat.id, "¿Qué te gustaría que te recomendara?", reply_markup=markup)
    bot.register_next_step_handler(msg, get_preference)

def get_preference(message):
    preference = message.text  # Aquí guardas la preferencia del usuario
    markup = types.ReplyKeyboardRemove()  # Preparas para quitar el teclado
    msg = bot.send_message(message.chat.id, "Por favor, envíame un mensaje sobre cómo te sientes.", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda msg: suggest_based_on_mood(msg, preference))

def suggest_based_on_mood(message, preference):
    user_sentiment_message = message.text  # Aquí tienes el mensaje del usuario sobre cómo se siente
    user_id = message.from_user.id

    # Aquí enviarías tanto el mensaje del usuario como la preferencia al endpoint /sugerencia
    response = requests.post(f"{API_URL}sugerencia", json={"message": user_sentiment_message, "preference": preference})
    if response.status_code == 200:
        recommendation = response.json()["recommendation"]
        bot.send_message(user_id, f"{recommendation}")
    else:
        bot.send_message(user_id, "Hubo un error al procesar tu solicitud.")


if __name__ == "__main__":
    bot.infinity_polling()