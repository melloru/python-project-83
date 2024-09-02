import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError
from typing import Literal


def get_db_connection(db_url):
    try:
        return psycopg2.connect(db_url)
    except OperationalError:
        print("Can't establish connection to the database")
    except Exception as e:
        print(f"An error occurred: {e}")


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        self.conn.commit()

    def query_processing(self, query, get_data: Literal['one', 'all'],
                         params=None):
        if get_data not in ['one', 'all']:
            raise ValueError("Parameter 'get' must be either 'one' or 'all'.")

        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute(query, params)
            return curs.fetchone() if get_data == 'one' else curs.fetchall()

    def find_url(self, url_id=None, url_name=None):
        query = """
            SELECT * FROM urls
            WHERE {}
            LIMIT 1;
            """.format('name = %(url_name)s' if url_name else 'id = %(url_id)s')
        params = {'url_name': url_name} if url_name else {'url_id': url_id}
        return self.query_processing(query, 'one', params=params)

    def add_url(self, url):
        query = """INSERT INTO urls (name)
                        VALUES (%(url)s)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING *;"""
        params = {'url': url}
        return self.query_processing(query, 'one', params=params)

    def get_urls(self):
        query = 'SELECT * FROM urls ORDER BY id DESC;'
        return self.query_processing(query, 'all')
