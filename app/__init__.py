from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login.login_view = "login"
login.login_message = u"Por favor autentíquese para poder usar la aplicación."
from app import routes, models

db.create_all()
