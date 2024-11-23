import sqlite3


class TicketBookWorm:
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
        self.conn.commit()

    def clean_up_ticket_vault(self):
        self.cursor.execute('DELETE FROM ticket')
        self.conn.commit()

    def regist_ticket(self, code):
        self.cursor.execute('INSERT INTO ticket (codigo) VALUES (?)', (code,))
        self.conn.commit()

    def update_status(self, code):
        self.cursor.execute(
            '''UPDATE ticket SET estado = 'ASIGNADO' WHERE codigo = ?''',
            (code,)
        )
        self.conn.commit()

    def check_ticket(self, code):
        self.cursor.execute('''SELECT * FROM ticket WHERE codigo = ? AND estado = 'DISPONIBLE' ''', (code,))
        ticket = self.cursor.fetchone()
        if ticket:
            self.update_status(ticket[0])
            return True
        else:
            return False

    def get_total_register_number(self):
        self.cursor.execute('''SELECT COUNT(*) FROM ticket''')
        return self.cursor.fetchone()[0]

    def get_total_register_available_number(self):
        self.cursor.execute('''SELECT COUNT(*) FROM ticket WHERE estado = "DISPONIBLE"''')
        return self.cursor.fetchone()[0]

    def check_session(self):
        total_registers = int(self.get_total_register_number())
        if total_registers == 750 or total_registers == 1000:
            return False
        else:
            return True

    def seal_vault(self):
        self.conn.commit()
        self.conn.close()