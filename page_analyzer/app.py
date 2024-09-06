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

    message, id = add_url(url_data)
    if message == 'danger':
        flash(*messages['danger'])
        session['url'] = url_data['name']
        return redirect(url_for('index'))

    session.pop('url', None)

    flash(*messages[message])
    return redirect(url_for('url_show', id=id))


@app.get('/urls/<int:id>')
def url_show(id):
    message = get_flashed_messages(with_categories=True)

    url = get_url(id)
    if url == 404:
        return render_template('page_not_found.html')

    checks = get_url_checks(id)
    return render_template('show.html',
                           messages=message,
                           url=url,
                           checks=checks)


@app.post('/urls/<int:id>/checks')
def url_check(id):
    messages = {
        'danger': ('Произошла ошибка при проверке', 'danger'),
        'success': ('Страница успешно проверена', 'success'),
    }

    url = request.form.get('url_name')
    check = add_url_check(id, url)

    if check == 'danger':
        flash(*messages['danger'])
        return redirect(url_for('url_show', id=id))

    if check == 'success':
        flash(*messages['success'])
        return redirect(url_for('url_show', id=id))
