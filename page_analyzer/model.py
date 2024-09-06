from page_analyzer.db import UrlRepository
from page_analyzer.validator import validate
from bs4 import BeautifulSoup
import requests


repo = UrlRepository()


def find_url(id):
    found_url = repo.select_url(url_id=id)
    if not found_url:
        return 404
    return found_url


def find_url_checks(id):
    founded_checks = repo.select_url_checks(id)
    return founded_checks


def get_urls():
    urls = repo.select_urls()
    return urls


def add_url(url):
    verified_url = validate(url['name'])
    if verified_url.get('error_name'):
        return 'danger', 0

    found_url = repo.select_url(url_name=verified_url['netloc'])

    if found_url:
        return 'info', found_url['id']

    added_url = repo.insert_url(verified_url['netloc'])
    return 'success', added_url['id']


def add_url_check(id, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception:
        return 'danger'

    if response.status_code == 200:
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
