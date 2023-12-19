import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, db_host, db_port, db_user, db_pass, db_name):
        try:
            self.connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                passwd=db_pass,
                database=db_name
            )
            if self.connection.is_connected():
                print("Conexión a la base de datos establecida.")
        except Error as e:
            print("Error al conectar a MySQL", e)

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada.")

    def execute_query(self, query, data):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            print(cursor.rowcount, "registro insertado.")
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")

    def insert_user_log(self, data):
        print("Insertando registro en user_log...")
        query = """
        INSERT INTO user_log (user_id, username, command_time, date, command)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            log_id = cursor.lastrowid
            print("Registro insertado en user_log con log_id:", log_id)
            return log_id
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None

    def insert_status(self, data):
        # Verificar si ya existe un estado del servicio en la base de datos
        existing_status = self.get_status()
        if existing_status is None:
            # Insertar nuevo registro
            print("Insertando nuevo estado del servicio...")
            query = """
            INSERT INTO service_status (service_name, version, log_level, status, models_info)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.execute_query(query, (data['service_name'], data['version'], data['log_level'], data['status'], data['models_info']))
        else:
            # Opcional: Actualizar el registro existente
            print("Actualizando estado del servicio existente...")
            query = """
            UPDATE service_status
            SET service_name = %s, version = %s, log_level = %s, status = %s, models_info = %s
            WHERE id = %s
            """
            self.execute_query(query, (data['service_name'], data['version'], data['log_level'], data['status'], data['models_info'], existing_status['id']))

            
    def insert_sentiment(self, log_id, texto_analizado, label, score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu):
        query = """
        INSERT INTO sentiment (log_id, texto_analizado, label, score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (log_id, texto_analizado, label, score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        self.execute_query(query, data)

    def insert_analysis(self, log_id, texto_analizado, pos_tags_resumen, pos_tags_conteo, ner_resumen, ner_conteo, sentimiento_label, sentimiento_score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu):
        query = """
        INSERT INTO analysis (log_id, texto_analizado, pos_tags_resumen, pos_tags_conteo, ner_resumen, ner_conteo, sentimiento_label, sentimiento_score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (log_id, texto_analizado, pos_tags_resumen, pos_tags_conteo, ner_resumen, ner_conteo, sentimiento_label, sentimiento_score, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            print("Registro insertado en analysis con éxito.")
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")

    def get_user_ids(self):
        print("Obteniendo user_ids...")
        query = "SELECT DISTINCT user_id FROM user_log"
        user_ids = set()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                user_ids = {row[0] for row in result}
        except Error as e:
            print(f"Error al obtener los user_ids: {e}")
        return user_ids
    
    def get_log_id(self, user_id):
        print(f"Obteniendo el último log_id para el user_id {user_id}...")
        query = """
        SELECT log_id FROM user_log
        WHERE user_id = %s
        ORDER BY command_time DESC
        LIMIT 1
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]  # Retorna el log_id más reciente
                else:
                    print("No se encontraron registros de log para este user_id.")
                    return None
        except Error as e:
            print(f"Error al obtener log_id: {e}")
            return None

    def get_status(self):
        query = "SELECT * FROM service_status LIMIT 1"
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchone()
        except Error as e:
            print(f"Error al obtener el estado del servicio: {e}")
            return None

    def insert_personalized_response(self, log_id, sentiment_label, response_message, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu):
        query = """
        INSERT INTO personalized_response (log_id, user_id, sentiment_label, response_message, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (log_id, sentiment_label, response_message, fecha_hora, tiempo_ejecucion, modelos, longitud_texto, uso_memoria, uso_cpu)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            print("Registro insertado en personalized_response con éxito.")
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")