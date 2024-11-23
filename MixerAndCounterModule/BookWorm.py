import sqlite3

class BookWorm:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """Establece una conexión con la base de datos."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()

    def fetch_records(self, table_name):
        """Obtiene los registros de la tabla especificada."""
        try:
            self.connect()
            self.cursor.execute(f"SELECT * FROM {table_name}")
            records = self.cursor.fetchall()
            return records
        except sqlite3.Error as e:
            print(f"Error al obtener registros: {e}")
            return []
        finally:
            self.close()
