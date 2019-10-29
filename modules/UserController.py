import sqlite3


class UserController:
    def __init__(self, data_base):
        self.conn = sqlite3.connect(data_base)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (username text, password text)")
        self.conn.commit()

    def insert_record(self, records=None):
        self.cur.executemany("INSERT INTO users VALUES "
                             "(?, ?)", records)
        self.conn.commit()

    def show_records(self):
        for row in self.cur.execute('SELECT * FROM users'):
            print(row)

    def get_record(self):
        for row in self.cur.execute('SELECT * FROM users'):
            return row

    def get_filtered_records(self, username):
        all_rows = []
        for row in self.cur.execute('SELECT * FROM users '
                                    'where username = ?', (username,)):
            all_rows.append(row)
        return all_rows

    def close_connection(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    db = UserController('users.sql')
    print(db.get_record()[0])
    db.close_connection()