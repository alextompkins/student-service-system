# Importing Flask, SQLAlchemy and LoginManager
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# Flask App and SQLAlchemy Initialisation
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Login Manager Initialisation
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "message"
login_manager.init_app(app)

# Load views, models
from serviceapp import views, models

# Start Flask app
if __name__ == '__main__':
	app.run(
		debug=True
	)
