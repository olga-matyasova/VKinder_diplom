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

    def create_table(self, user_info_id, item_id):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS results (user_info_id INT PRIMARY KEY, item_id INT PRIMARY KEY)')

    def save_result(self, result):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('INSERT INTO results (user_info_id, item_id) VALUES (%s, %s)', result)

    def check_user_id_database(self, user_info-id, item_id):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM results WHERE user_info_id = %s AND item_id = %s', (user_info_id, item_id))
                return cur.fetchone() is not None

    def close(self):
        if self.conn is not None:
            self.conn.close()