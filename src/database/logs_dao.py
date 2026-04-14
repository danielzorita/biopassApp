from src.database.connection import DBConnection
from datetime import datetime

class AccessLogDAO:
    
    @staticmethod
    def crear_tabla():
        cursor = DBConnection.get_cursor()
        db_type = DBConnection.DB_TYPE
        
        try:
            if db_type == "postgres":
                sql = """
                CREATE TABLE IF NOT EXISTS access_logs (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100),
                    status VARCHAR(50), -- 'SUCCESS', 'DENIED', 'LIVENESS_FAILED'
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            else:
                sql = """
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            cursor.execute(sql)
            DBConnection.commit()
        except Exception as e:
            print(f"Error creando tabla access_logs: {e}")

    @staticmethod
    def registrar_acceso(nombre, status):
        AccessLogDAO.crear_tabla()
        cursor = DBConnection.get_cursor()
        try:
            sql = "INSERT INTO access_logs (nombre, status) VALUES (?, ?)"
            if DBConnection.DB_TYPE == "postgres":
                sql = "INSERT INTO access_logs (nombre, status) VALUES (%s, %s)"
            
            cursor.execute(sql, (nombre, status))
            DBConnection.commit()
        except Exception as e:
            DBConnection.rollback()
            print(f"Error al registrar log: {e}")

    @staticmethod
    def obtener_logs(limit=50):
        AccessLogDAO.crear_tabla()
        cursor = DBConnection.get_cursor()
        try:
            sql = f"SELECT id, nombre, status, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT {limit}"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener logs: {e}")
            return []
