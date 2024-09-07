from page_analyzer.db import UrlRepository
from page_analyzer.validator import validate
from bs4 import BeautifulSoup
import requests


class DataBaseManager:
    def __init__(self):
        self.repo = None

    def __enter__(self):
        self.repo = UrlRepository()
        return self.repo

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.repo:
            self.repo.close()


def get_url(id):
    with DataBaseManager() as repo:
        found_url = repo.select_url(url_id=id)
        if not found_url:
            return 404
        return found_url


def get_url_checks(id):
    with DataBaseManager() as repo:
        founded_checks = repo.select_url_checks(id)
        return founded_checks


def get_urls():
    with DataBaseManager() as repo:
        urls = repo.select_urls()
        return urls


def add_url(url):
    with DataBaseManager() as repo:
        verified_url = validate(url)
        if verified_url.get('error_name'):
            return 'danger', 0
        found_url = repo.select_url(url_name=verified_url['name'])
        if found_url:
            return 'info', found_url['id']
        added_url = repo.insert_url(verified_url['name'])
        return 'success', added_url['id']


def add_url_check(id, url):
    with DataBaseManager() as repo:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception:
            return 'danger'

        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.find('h1')
        title = soup.find('title')
        content = soup.find('meta', attrs={'name': 'description'})

        result = {
            'id': id,
            'status_code': response.status_code,
            'h1': h1.get_text() if h1 else None,
            'title': title.get_text() if title else None,
            'content': content['content']
            if content and 'content' in content.attrs else None
            }
        repo.insert_url_check(result)
        return 'success'
