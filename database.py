import psycopg2
from config import DATABASE_URL


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Ошибка подключения к базе данных: {error}')

    def create_table(self):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS results (user_id INT, matched_user_id INT)')

    def save_result(self, result):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('INSERT INTO results (user_id, matched_user_id) VALUES (%s, %s)', result)

    def check_user_in_database(self, user_id, matched_user_id):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM results WHERE user_id = %s AND matched_user_id = %s',
                            (user_id, matched_user_id))
                return cur.fetchone() is not None

    def close(self):
        if self.conn is not None:
            self.conn.close()
