from flask import (Flask, request,
                   render_template, redirect,
                   flash, url_for, get_flashed_messages, session,
                   )
from page_analyzer.model import (add_url, get_url,
                                 get_url_checks, add_url_check,
                                 get_urls)
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    url = session.get('url', '')
    message = get_flashed_messages(with_categories=True)
    return render_template('index.html',
                           messages=message,
                           url=url)


@app.get('/urls')
def urls_get():
    urls = get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    messages = {
        'danger': ('Некорректный URL', 'danger'),
        'success': ('Страница успешно добавлена', 'success'),
        'info': ('Страница уже существует', 'info')
    }

    url_data = request.form.to_dict()

    status_of_addition, id = add_url(url_data['url'])
    if status_of_addition == 'danger':
        flash(*messages[status_of_addition])
        session['url'] = url_data['url']
        return redirect(url_for('index'))

    session.pop('url', None)

    flash(*messages[status_of_addition])
    return redirect(url_for('url_show', id=id))


@app.get('/urls/<int:id>')
def url_show(id):
    messages = get_flashed_messages(with_categories=True)

    url = get_url(id)
    if url == 404:
        return render_template('page_not_found.html')

    checks = get_url_checks(id)
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
    status_check = add_url_check(id, url)

    if status_check == 'danger':
        flash(*messages[status_check])
        return redirect(url_for('url_show', id=id))

    if status_check == 'success':
        flash(*messages[status_check])
        return redirect(url_for('url_show', id=id))
