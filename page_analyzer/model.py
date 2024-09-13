from page_analyzer.db import SelectRepository, InsertRepository
from page_analyzer.validator import validate
from bs4 import BeautifulSoup
import requests


class DataBaseManager:
    """Управление соединением с базой данных"""
    def __init__(self, repo_cls):
        self.repo = None
        self.repo_cls = repo_cls

    def __enter__(self):
        self.repo = self.repo_cls()
        return self.repo

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.repo:
            self.repo.close()


class UrlRetrievalService:
    """Служба поиска URL"""
    def get_url(self, url_id):
        with DataBaseManager(SelectRepository) as repo:
            found_url = repo.select_url(url_id=url_id)
            if not found_url:
                return 404
            return found_url

    def get_urls(self):
        with DataBaseManager(SelectRepository) as repo:
            return repo.select_urls()


class UrlManagementService:
    """Служба управления URL-адресами"""
    def add_url(self, url):
        verified_url = validate(url)
        if verified_url.get('error_name'):
            return 'danger', 0

        with DataBaseManager(SelectRepository) as repo:
            found_url = repo.select_url(url_name=verified_url['name'])
            if found_url:
                return 'info', found_url['id']

        with DataBaseManager(InsertRepository) as repo:
            added_url = repo.insert_url(verified_url['name'])
            return 'success', added_url['id']


class CheckRetrievalService:
    """Служба поиска проверок"""
    def get_url_checks(self, id):
        with DataBaseManager(SelectRepository) as repo:
            return repo.select_url_checks(id)


class UrlCheckService:
    """Служба проверки URL"""
    def add_url_check(self, url_id, url):
        try:
            response = self.fetch_url(url)
        except Exception:
            return 'danger'

        result = self.parse_response(response, url_id)

        with DataBaseManager(InsertRepository) as repo:
            repo.insert_url_check(result)

        return 'success'

    @staticmethod
    def fetch_url(url):
        """Получение данных URL"""
        response = requests.get(url)
        response.raise_for_status()
        return response

    @staticmethod
    def parse_response(response, url_id):
        """Анализ ответа"""
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.find('h1')
        title = soup.find('title')
        content = soup.find('meta', attrs={'name': 'description'})

        return {
            'id': url_id,
            'status_code': response.status_code,
            'h1': h1.get_text() if h1 else None,
            'title': title.get_text() if title else None,
            'content': content['content']
            if content and 'content' in content.attrs else None
        }
