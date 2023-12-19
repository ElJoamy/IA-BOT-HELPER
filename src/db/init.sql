CREATE DATABASE IF NOT EXISTS VirtualDB;
USE VirtualDB;

CREATE TABLE IF NOT EXISTS user_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    command_time DATETIME NOT NULL,
    date DATE NOT NULL,
    command VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS sentiment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT NOT NULL,
    texto_analizado TEXT NOT NULL,
    label VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    tiempo_ejecucion FLOAT NOT NULL,
    modelos VARCHAR(255) NOT NULL,
    longitud_texto INT NOT NULL,
    uso_memoria INT NOT NULL,
    uso_cpu FLOAT NOT NULL,
    FOREIGN KEY (log_id) REFERENCES user_log(log_id)
);

CREATE TABLE IF NOT EXISTS analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT NOT NULL,
    texto_analizado TEXT NOT NULL,
    pos_tags_resumen TEXT NOT NULL,
    pos_tags_conteo TEXT NOT NULL,
    ner_resumen TEXT NOT NULL,
    ner_conteo TEXT NOT NULL,
    sentimiento_label VARCHAR(50) NOT NULL,
    sentimiento_score FLOAT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    tiempo_ejecucion FLOAT NOT NULL,
    modelos VARCHAR(255) NOT NULL,
    longitud_texto INT NOT NULL,
    uso_memoria INT NOT NULL,
    uso_cpu FLOAT NOT NULL,
    FOREIGN KEY (log_id) REFERENCES user_log(log_id)
);

CREATE TABLE IF NOT EXISTS personalized_response (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT NOT NULL,
    sentiment_label VARCHAR(50) NOT NULL,
    response_message TEXT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    tiempo_ejecucion FLOAT NOT NULL,
    modelos VARCHAR(255) NOT NULL,
    longitud_texto INT NOT NULL,
    uso_memoria INT NOT NULL,
    uso_cpu FLOAT NOT NULL,
    FOREIGN KEY (log_id) REFERENCES user_log(log_id)
);

