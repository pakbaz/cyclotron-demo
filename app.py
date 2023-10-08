import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, json, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Joke

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    jokes = Joke.query.all()
    return render_template('index.html', jokes=jokes)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    joke = Joke.query.where(Joke.id == id).first()
    return render_template('details.html', joke=joke)

@app.route('/fetch', methods=['GET'])
def add_joke():
    # fetch a joke and save it to the database

    url = 'https://official-joke-api.appspot.com/random_joke'
    response = request.get(url)
    data = json.loads(response.text)

    # check if the same id exists in the database
    if Joke.query.where(Joke.id == data['id']).first():
        return redirect(url_for('index'))

    joke = Joke()
    joke.type = data['type']
    joke.setup = data['setup']
    joke.punchline = data['punchline']
    joke.fetchDate = datetime.now()
    joke.id = data['id']

    db.session.add(joke)
    db.session.commit()

    return redirect(url_for('details', id=joke.id))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
