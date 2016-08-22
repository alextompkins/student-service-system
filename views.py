# Include required Flask functions
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

# Include app objects from __init__.py and other app files
from serviceapp import app, db, login_manager
# TO BE IMPLEMENTED
#from .forms import LoginForm
from .models import User

# Include Python libraries for hashing and creating random hexes
import hashlib, uuid


# Helper Functions
def hash_password(password, salt=None):
	"""Returns a salted hash of a password, with the salt randomly generated if not given."""
	if not salt:
		salt = uuid.uuid4().hex
	return hashlib.sha256(password.encode() + salt.encode()).hexdigest()

def check_credentials(username, password):
	"""Returns True if the input credentials match the credentials of the user in the 
	database, False if they do not or if user does not exist in the database"""
	matching_user = User.query.filter(User.nickname == username).first()
	if matching_user:
		matching_hash, salt = matching_user.password.split(':')
		return hash_password(password, salt) == matching_hash
	else:
		return False


# Views
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',
							title='Home',
							)
