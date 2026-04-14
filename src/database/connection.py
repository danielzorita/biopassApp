import sqlite3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DBConnection:
    _connection = None
    DB_TYPE = os.getenv("DB_TYPE", "sqlite") # sqlite o postgres
    
    # Ruta absoluta para evitar que se cree en sitios diferentes
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SQLITE_PATH = os.path.join(BASE_DIR, "db", "biopass.db")

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            try:
                if cls.DB_TYPE == "postgres":
                    cls._connection = psycopg2.connect(
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD"),
                        host=os.getenv("DB_HOST", "localhost"),
                        port=os.getenv("DB_PORT", "5432")
                    )
                    print("✅ Conectado a PostgreSQL.")
                else:
                    cls._connection = sqlite3.connect(cls.SQLITE_PATH, check_same_thread=False)
                    print(f"✅ Conectado a SQLite ({cls.SQLITE_PATH}).")
            except Exception as e:
                print(f"❌ Error de conexión DB ({cls.DB_TYPE}): {e}")
                raise e
        return cls._connection

    @classmethod
    def get_cursor(cls):
        conn = cls.get_connection()
        return conn.cursor()

    @classmethod
    def commit(cls):
        if cls._connection:
            cls._connection.commit()

    @classmethod
    def rollback(cls):
        if cls._connection:
            cls._connection.rollback()
