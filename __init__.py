# Importing Flask, SQLAlchemy and LoginManager
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# Flask App and SQLAlchemy Initialisation
app = Flask(__name__)
app.config.from_object('serviceapp_config')
db = SQLAlchemy(app)

# Login Manager Initialisation
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "message"
login_manager.init_app(app)

# Starting App
from serviceapp import views, models

app.run(
	debug=True
)
