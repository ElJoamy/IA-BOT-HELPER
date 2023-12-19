Crear un archivo `README.md` detallado para un proyecto como el tuyo es fundamental para su comprensión y uso efectivo. Aquí tienes un esquema que puedes seguir, adaptándolo a las necesidades específicas de tu proyecto:

---

# Nombre del Proyecto: AssistBot API AI with Telegram

## Descripción

Este proyecto consiste en un bot de Telegram integrado con una API de inteligencia artificial. Utiliza OpenAI y Spacy para análisis de sentimientos y generación de respuestas personalizadas basadas en el estado de ánimo del usuario. Incluye una base de datos MySQL para almacenar registros de usuario y análisis realizados.

## Características

- Análisis de sentimientos de textos.
- Respuestas personalizadas basadas en el estado de ánimo.
- Recomendaciones de libros, videos, canciones, etc., según el sentimiento del usuario.
- Registro de actividades en base de datos MySQL.

## Estructura del Proyecto

```bash
D:.
│   .env
│   .gitignore
│   Dockerfile
│   README.md
│   requirements.txt
│   tree.txt
│   
└───src
    │   app.py
    │   config.py
    │   response_models.py
    │   sentiment.py
    │   telegram_bot.py
    │   
    └───db
            db_manage.py
            init.sql
```

## Modelo Entidad-Relación

- ![Modelo Entidad-Relación](/media/modeloer/ModeloER.png)

### Entidades

- **service_status**: Contiene información sobre el estado del servicio, como el nombre, la versión y el nivel de log. La columna `id` parece ser una clave primaria que identifica de manera única cada registro.

- **user_log**: Registra los comandos ejecutados por los usuarios y cuándo se ejecutaron. `user_id` y `log_id` son campos importantes aquí, siendo `log_id` la clave primaria.

- **sentiment**: Almacena los resultados del análisis de sentimientos realizado en los textos. Incluye etiquetas de sentimiento, puntuaciones y uso de recursos como memoria y CPU. La clave primaria es `id`, y se relaciona con `user_log` a través de `log_id`.

- **personalized_response**: Guarda las respuestas personalizadas generadas para los usuarios, basadas en el análisis de sentimientos. Se vincula con `user_log` usando `log_id` y con `user_log` a través de `user_id`.

- **analysis**: Parece ser una tabla adicional para almacenar un análisis más detallado de los textos, posiblemente con etiquetas de partes del discurso (POS) y entidades nombradas (NER). Se relaciona con `user_log` por `log_id`.

### Relaciones

- La relación entre `user_log` y `sentiment` es de uno a uno, lo que indica que para cada log de usuario hay un único análisis de sentimiento correspondiente.

- La relación entre `user_log` y `personalized_response` es de uno a uno, sugiriendo que para cada log de usuario hay una respuesta personalizada.

- La relación entre `user_log` y `analysis` también es de uno a uno, lo que implica que cada entrada en `user_log` tiene un análisis detallado correspondiente.

### Consideraciones

- La presencia de `log_id` como clave foránea en varias tablas indica que las acciones de los usuarios y los análisis realizados están estrechamente vinculados a registros de log específicos.

- Las columnas `user_id` en `user_log` y `personalized_response` sugieren que las respuestas personalizadas pueden rastrearse hasta usuarios individuales.

- Los campos `fecha_hora` y `tiempo_ejecucion` en varias tablas probablemente se utilizan para registrar cuándo se llevó a cabo una acción y cuánto tiempo tomó.

- Las columnas `uso_memoria` y `uso_cpu` podrían utilizarse para monitorear el rendimiento y los recursos consumidos por cada operación.

Este modelo facilita un seguimiento detallado de la interacción de los usuarios con el bot, permitiendo un análisis profundo de las preferencias y respuestas emocionales de los usuarios, así como la eficiencia del sistema en términos de recursos de cómputo utilizados.

## Pre-requisitos

- Python 3.8 o superior.
- MySQL 8.0 o superior.
- Token de OpenAI.
- Token de Telegram Bot. si no tienes uno, puedes seguir [estos pasos](tutorial/CreateBotTelegram.md) para crear uno.

## Instalación

1. Clone el repositorio a su máquina local.
2. Instale las dependencias con `pip install -r requirements.txt`.
3. Configure su base de datos MySQL y actualice las credenciales en `.env`.
4. Ejecute `uvicorn src.app:app --reload` para iniciar el servidor.
5. Ejecute `python src.telegram` para iniciar el bot de Telegram.

## Uso

El bot de Telegram responderá a varios comandos:

- `/start`: Inicia la interacción con el bot.
- `/help`: Muestra información de ayuda.
- `/status`: Muestra el estado actual del servicio.
- `/sentiment`: Realiza un análisis de sentimiento del texto proporcionado.
- `/amigo`: Genera un mensaje personalizado basado en el estado de ánimo.
- `/sugerencia`: Proporciona sugerencias basadas en el estado de ánimo.

## Configuración

### Archivo `.env`

Este archivo contiene variables de entorno esenciales para la configuración. Asegúrese de actualizar este archivo con sus propias claves y configuraciones.

puedes ver un ejemplo en el archivo [.env.example](.env.example).
```.env
SERVICE_NAME=AssistBot API AI with Telegram Prueba
K_REVISION=NOT DEPLOYED
LOG_LEVEL=DEBUG
OPENAI_KEY=your_api_key
TELEGRAM_TOKEN=your_telegram_token
#API_URL=
DB_HOST=your_db_host
DB_PORT=3303
DB_USER=root
DB_PASS=root
DB_NAME=your_db_name
```

## Contribuir

Las contribuciones al proyecto son bienvenidas. Para contribuir:

1. Haga un fork del proyecto.
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`).
3. Haga commit de sus cambios (`git commit -m 'Add some AmazingFeature'`).
4. Haga push a la rama (`git push origin feature/AmazingFeature`).
5. Abra una Pull Request.

## Licencia

Este proyecto está bajo la MIT License. Ver [LICENSE](LICENSE) para más detalles.

