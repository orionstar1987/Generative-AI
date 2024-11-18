"""_init__.py"""

from flask import Flask
from flask_injector import FlaskInjector
from .logger import AppLogger
from .config import Config
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
from flasgger import Swagger

status = load_dotenv(find_dotenv(filename=".env.local"))
print(status)
app = Flask(__name__, static_folder="../static", static_url_path="/")
Swagger(app)
CORS(app)
with app.app_context():
    from . import routes


def create_app():
    """Create app with flask injector"""
    AppLogger.enable_flask(app)
    FlaskInjector(app=app, modules=[Config.configure])
    return app
