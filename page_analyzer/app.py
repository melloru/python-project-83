from flask import (Flask, request,
                   render_template, redirect,
                   flash, url_for, get_flashed_messages, session,
                   )
from page_analyzer.model import (UrlCheckService, UrlRetrievalService,
                                 UrlManagementService, CheckRetrievalService)
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

url_retrieval_service = UrlRetrievalService()
url_management_service = UrlManagementService()
check_retrieval_service = CheckRetrievalService()
url_check_service = UrlCheckService()


@app.route('/')
def index():
    message = get_flashed_messages(with_categories=True)
    return render_template('index.html',
                           messages=message)


@app.get('/urls')
def urls_get():
    urls = url_retrieval_service.get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    messages = {
        'danger': ('danger', 'Некорректный URL'),
        'success': ('Страница успешно добавлена', 'success'),
        'info': ('Страница уже существует', 'info')
    }

    url_data = request.form.to_dict()

    status_of_addition, id = url_management_service.add_url(url_data['url'])

    if status_of_addition == 'danger':
        message = [messages[status_of_addition]]
        session['url'] = url_data['url']
        return render_template('index.html',
                               messages=message,
                               url=url_data['url']), 422

    flash(*messages[status_of_addition])
    return redirect(url_for('url_show', id=id))


@app.get('/urls/<int:id>')
def url_show(id):
    messages = get_flashed_messages(with_categories=True)

    url = url_retrieval_service.get_url(id)
    if url == 404:
        return render_template('page_not_found.html')

    checks = check_retrieval_service.get_url_checks(id)
    return render_template('show.html',
                           messages=messages,
                           url=url,
                           checks=checks)


@app.post('/urls/<int:id>/checks')
def url_check(id):
    messages = {
        'danger': ('Произошла ошибка при проверке', 'danger'),
        'success': ('Страница успешно проверена', 'success'),
    }

    url = request.form.get('url_name')
    status_check = url_check_service.add_url_check(id, url)

    if status_check == 'danger':
        flash(*messages[status_check])
        return redirect(url_for('url_show', id=id))

    if status_check == 'success':
        flash(*messages[status_check])
        return redirect(url_for('url_show', id=id))
