from flask import (Flask, request,
                   render_template, redirect,
                   flash, url_for, get_flashed_messages,
                   )
from page_analyzer.db import UrlRepository, get_db_connection
from page_analyzer.validator import validate
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

conn = get_db_connection(DATABASE_URL)
repo = UrlRepository(conn)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html',
                           messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def urls_index():
    if request.method == "POST":
        url_data = request.form.to_dict()
        parsed_url = validate(url_data['name'])

        if parsed_url.get('error_name'):
            flash(parsed_url['error_name'], 'danger')
            return redirect(url_for('index'))

        found_url = repo.find_url(url_name=parsed_url['name'])

        if found_url:
            flash('Страница уже существует', 'info')
            return redirect(url_for('urls_show', id=found_url['id']))
        else:
            added_url = repo.add_url(parsed_url['name'])
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('urls_show', id=added_url['id']))

    urls = repo.get_urls()
    print(urls)
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def urls_show(id):
    messages = get_flashed_messages(with_categories=True)
    found_url = repo.find_url(url_id=id)
    if not found_url:
        return render_template('page_not_found.html')
    found_checks = repo.get_url_checks(id)
    return render_template('show.html',
                           messages=messages,
                           url=found_url,
                           checks=found_checks)


@app.post('/urls/<int:id>/checks')
def start_url_check(id):
    try:
        url = request.form.get('url_name')
        response = requests.get(url)
        response.raise_for_status()
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('urls_show', id=id))

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
        repo.url_check(result)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_show', id=id))
