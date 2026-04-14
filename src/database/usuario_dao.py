from src.database.connection import DBConnection

class UsuarioDAO:
    
    @staticmethod
    def crear_tabla():
        cursor = DBConnection.get_cursor()
        db_type = DBConnection.DB_TYPE
        
        try:
            if db_type == "postgres":
                sql = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    foto_cara BYTEA NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            else:
                sql = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    foto_cara BLOB NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            cursor.execute(sql)
            DBConnection.commit()
        except Exception as e:
            print(f"Error creando tabla usuarios: {e}")

    @staticmethod
    def registrar_usuario(nombre, cara_bytes):
        UsuarioDAO.crear_tabla()
        cursor = DBConnection.get_cursor()
        try:
            sql = "INSERT INTO usuarios (nombre, foto_cara) VALUES (?, ?)"
            if DBConnection.DB_TYPE == "postgres":
                sql = "INSERT INTO usuarios (nombre, foto_cara) VALUES (%s, %s)"
            
            cursor.execute(sql, (nombre, cara_bytes))
            DBConnection.commit()
            return True
        except Exception as e:
            DBConnection.rollback()
            print(f"Error al registrar usuario: {e}")
            return False

    @staticmethod
    def obtener_todos():
        UsuarioDAO.crear_tabla()
        cursor = DBConnection.get_cursor()
        try:
            sql = "SELECT id, nombre, foto_cara FROM usuarios ORDER BY id DESC"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []

    @staticmethod
    def eliminar_usuario(user_id):
        cursor = DBConnection.get_cursor()
        try:
            sql = "DELETE FROM usuarios WHERE id = ?"
            if DBConnection.DB_TYPE == "postgres":
                sql = "DELETE FROM usuarios WHERE id = %s"
            
            cursor.execute(sql, (user_id,))
            DBConnection.commit()
            return True
        except Exception as e:
            DBConnection.rollback()
            print(f"Error al eliminar usuario: {e}")
            return False
