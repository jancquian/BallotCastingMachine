import sqlite3


class BookWorm:
    def __init__(self, path):
        self.path_data_base = str(path)
        self.conn = sqlite3.connect(str(path) + '/session.db')
        self.cursor = self.conn.cursor()

    def start_up_ticket_vault(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket (
            codigo TEXT PRIMARY KEY,
            estado TEXT NOT NULL DEFAULT 'DISPONIBLE')
        ''')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS last_ticket (codigo TEXT PRIMARY KEY)')
        self.conn.commit()

    def clean_up_ticket_vault(self):
        self.cursor.execute('DELETE FROM ticket')
        self.cursor.execute('DELETE FROM last_ticket')
        self.conn.commit()

    def regist_ticket(self, code):
        self.cursor.execute('INSERT INTO ticket (codigo) VALUES (?)', (code,))
        self.conn.commit()

    def regist_last_ticket(self, code):
        self.cursor.execute('INSERT INTO last_ticket (codigo) VALUES (?)', (code,))
        self.conn.commit()

    def update_status(self, code):
        self.cursor.execute(
            '''UPDATE ticket SET estado = 'ASIGNADO' WHERE codigo = ?''',
            (code,)
        )
        self.conn.commit()

    def update_last_ticket(self, old_ticket, new_ticket):
        self.cursor.execute(
            '''UPDATE last_ticket SET codigo = (?) WHERE codigo = (?)''',
            (new_ticket, old_ticket)
        )
        self.conn.commit()

    def get_ticket(self):
        self.cursor.execute('''SELECT * FROM ticket WHERE estado = 'DISPONIBLE' LIMIT 1''')
        ticket = self.cursor.fetchone()
        if ticket:
            self.update_status(ticket[0])
            return ticket[0]
        else:
            return "NONE"

    def get_last_ticket(self):
        self.cursor.execute('''SELECT * FROM last_ticket LIMIT 1''')
        ticket = self.cursor.fetchone()
        if ticket:
            self.update_status(ticket[0])
            return ticket[0]
        else:
            return "NONE"

    def get_total_register_number(self):
        self.cursor.execute('''SELECT COUNT(*) FROM ticket''')
        return self.cursor.fetchone()[0]

    def get_total_register_available_number(self):
        self.cursor.execute('''SELECT COUNT(*) FROM ticket WHERE estado = "DISPONIBLE"''')
        return self.cursor.fetchone()[0]

    def seal_vault(self):
        self.conn.commit()
        self.conn.close()