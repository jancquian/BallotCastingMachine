import sqlite3


class BookWorm:
    def __init__(self, path):
        self.path_data_base = str(path)
        self.conn = sqlite3.connect(str(path) + '/vault.db')
        self.cursor = self.conn.cursor()

    def start_up_vault(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS conteo (
            id TEXT PRIMARY KEY,
            resultado TEXT NOT NULL,
            firma TEXT NOT NULL)
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voto TEXT NOT NULL,
            firma TEXT NOT NULL)
        ''')
        self.conn.commit()

    def clean_up_vault(self):
        self.cursor.execute('DELETE FROM conteo')
        self.cursor.execute('DELETE FROM votos')
        self.conn.commit()

    def check_data_base(self):
        self.start_up_vault()
        self.cursor.execute('''SELECT COUNT(*) FROM conteo''')
        result = self.cursor.fetchone()
        if result:
            if result[0] >= 2:
                return True
            else:
                self.clean_up_vault()
                return False
        else:
            self.clean_up_vault()
            return False

    def regist_vote(self, vote, signature):
        self.cursor.execute('INSERT INTO votos (voto, firma) VALUES (?, ?)', (vote, signature))
        self.conn.commit()

    def regist_results(self,code, result, signature):
        self.cursor.execute(
            'INSERT INTO conteo (id, resultado, firma) VALUES (?, ?, ?)',
            (code, result, signature)
        )
        self.conn.commit()

    def update_results(self, code, new_result, new_signature):
        self.cursor.execute(
            'UPDATE conteo SET resultado = ?, firma = ? WHERE id = ?',
            (new_result, new_signature, code)
        )
        self.conn.commit()

    def get_precount(self, candidate_code):
        self.cursor.execute('''SELECT resultado FROM conteo WHERE id=?''', (candidate_code,))
        return self.cursor.fetchall()

    def get_recount_registers(self):
        self.cursor.execute('''SELECT * FROM conteo''')
        return self.cursor.fetchall()

    def seal_vault(self):
        self.conn.commit()
        self.conn.close()