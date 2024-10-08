import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError
from typing import Literal
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class DataBaseConnection:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = self.get_db_connection(db_url)

    def get_db_connection(self, db_url):
        try:
            return psycopg2.connect(db_url)
        except OperationalError:
            print("Can't establish connection to the database")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        if self.conn:
            self.conn.close()


class Repository:
    def __init__(self):
        self.connection = DataBaseConnection(DATABASE_URL)

    def commit(self):
        self.connection.conn.commit()

    def close(self):
        self.connection.close()

    def query_processing(self, query, get_data: Literal['one', 'all'] = None,
                         params=None):
        with self.connection.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute(query, params)
            self.commit()
            if get_data is None:
                return
            elif get_data not in ['one', 'all']:
                raise ValueError("""
                Parameter 'get' must be either
                'one' or 'all'.
                """)

            return curs.fetchone() if get_data == 'one' else curs.fetchall()


class SelectRepository(Repository):
    def select_url(self, url_id=None, url_name=None):
        query = """
            SELECT * FROM urls
            WHERE {}
            LIMIT 1;
            """.format('name = %(url_name)s' if url_name else 'id = %(url_id)s')
        params = {'url_name': url_name} if url_name else {'url_id': url_id}
        return self.query_processing(query, 'one', params=params)

    def select_urls(self):
        query = """
                SELECT u.id, u.name, uc.last_check, st_code.status_code
                FROM urls AS u
                LEFT JOIN (SELECT url_id, MAX(created_at) AS last_check
                FROM url_checks
                GROUP BY url_id) AS uc ON u.id = uc.url_id
                LEFT JOIN url_checks AS st_code
                ON u.id = st_code.url_id AND st_code.created_at = uc.last_check
                ORDER BY u.id DESC;"""

        return self.query_processing(query, 'all')

    def select_url_checks(self, url_id):
        query = """
        SELECT * FROM url_checks
        WHERE url_id = %(url_id)s
        ORDER BY id DESC;
        """
        params = {'url_id': url_id}
        return self.query_processing(query, 'all', params)


class InsertRepository(Repository):
    def insert_url(self, url):
        query = """
        INSERT INTO urls (name)
        VALUES (%(url)s)
        ON CONFLICT (name) DO NOTHING
        RETURNING *;
        """
        params = {'url': url}
        return self.query_processing(query, 'one', params=params)

    def insert_url_check(self, url):
        query = """
        INSERT INTO url_checks (url_id, status_code, h1, title, description)
        VALUES (%(id)s, %(status_code)s, %(h1)s, %(title)s, %(content)s);
        """
        params = {
            'id': url['id'],
            'status_code': url['status_code'],
            'h1': url['h1'],
            'title': url['title'],
            'content': url['content']
        }
        return self.query_processing(query, params=params)
