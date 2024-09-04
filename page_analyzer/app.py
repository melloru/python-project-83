from flask import (Flask, request,
                   render_template, redirect,
                   flash, url_for, get_flashed_messages,
                   )
from page_analyzer.db import UrlRepository, get_db_connection
from page_analyzer.validator import validate
from dotenv import load_dotenv
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
        errors = validate(url_data)

        if errors:
            flash(errors['name'], 'danger')
            return redirect(url_for('index'))

        found_url = repo.find_url(url_name=url_data['name'])

        if found_url:
            flash('Страница уже существует', 'info')
            return redirect(url_for('urls_show', id=found_url['id']))
        else:
            added_url = repo.add_url(url_data['name'])
            repo.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('urls_show', id=added_url['id']))

    urls = repo.get_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['GET', 'POST'])
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
    if not id:
        return "URL data is missing", 400
    print(id)
    repo.url_check(id)
    return redirect(url_for('urls_show', id=id))
