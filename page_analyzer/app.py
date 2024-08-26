from page_analyzer import app


@app.route('/')
def index():
    return 'Hello, World!'
