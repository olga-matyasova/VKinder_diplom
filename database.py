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
                cur.execute('CREATE TABLE IF NOT EXISTS result (user_id INT, best_match_id INT)')

    def save_result(self, user_id, best_match_id):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('INSERT INTO result (user_id, best_match_id) VALUES (%s, %s)', (user_id, best_match_id))

    def check_user_in_database(self, user_id, best_match_id):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM results WHERE user_id = %s AND best_match_id = %s',
                            (user_id, best_match_id))
                return cur.fetchone() is not None

    def close(self):
        if self.conn is not None:
            self.conn.close()
