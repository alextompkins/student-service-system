# Include required Flask functions
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required

# Include app objects from __init__.py and other app files
from serviceapp import app, db, login_manager
from .forms import LoginForm, CreateAccountForm, CreatePostAnyGroupForm, PostCommentForm
from .models import User, ServiceGroup, MemberLink, ServiceRecord, Post, PostComment, Application, ApplicationPart

# Include Python libraries for hashing and creating random hexes, also datetime and pytz for timestamp handling
import hashlib, uuid
from datetime import datetime, timedelta, tzinfo
from pytz import timezone, utc
LOCAL_TIMEZONE = timezone("Pacific/Auckland")


# Helper Functions
def hash_password(password, salt=None):
	"""Returns a salted hash of a password, with the salt randomly generated if not given."""
	if not salt:
		salt = uuid.uuid4().hex
	return hashlib.sha256(password.encode() + salt.encode()).hexdigest(), salt

def check_credentials(username, password):
	"""Returns True if the input credentials match the credentials of the user in the 
	database, False if they do not or if user does not exist in the database."""
	matching_user = User.query.filter(User.UserID == username).first()
	if matching_user:
		matching_hash, salt = matching_user.Password.split(':')
		return hash_password(password, salt)[0] == matching_hash
	else:
		return False

def get_recent_posts(user):
	"""Returns a tuple containing all of the posts from the current user's groups, sorted 
	backwards by date/time they were posted."""
	recent_posts = []
	for group in user.get_groups():
		for post in group.Posts:
			recent_posts.append(post)

	return sorted(recent_posts, key=lambda x: x.DateTimePosted)[::-1]

def format_local_time(utc_timestamp):
	"""Returns a formatted string of the given UTC date/time, converted to local timezone 
	and in a format based on how long ago versus current date/time."""
	local_timestamp = utc_timestamp.replace(tzinfo=utc).astimezone(LOCAL_TIMEZONE)
	current_timestamp = datetime.now(LOCAL_TIMEZONE)
	time_part = "{dt:%I}:{dt:%M} {dt:%p}".format(dt=local_timestamp).lstrip('0')

	if local_timestamp.year == current_timestamp.year:
		difference = current_timestamp - local_timestamp
		if (local_timestamp.month, local_timestamp.day) == (current_timestamp.month, current_timestamp.day):
			return "Today at {}".format(time_part)
		if (local_timestamp.month, local_timestamp.day) == (current_timestamp.month, current_timestamp.day - 1):
			return "Yesterday at {}".format(time_part)
		elif difference < timedelta(days=7):
			return "{} days ago at {}".format(difference.days, time_part)
		else:
			return "{}, {dt:%A} {dt.day} {dt:%B}".format(time_part, dt=local_timestamp)
	else:
		return "{}, {dt:%A}, {dt.day} {dt:%B} {dt:%Y}".format(time_part, dt=local_timestamp)


# Views
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	recent_posts = get_recent_posts(current_user)

	post_form = CreatePostAnyGroupForm()
	post_form.group.choices = [(str(group.GroupID), group.Name) for group in current_user.get_groups()]
	comment_form = PostCommentForm()

	if request.method == 'POST':
		if post_form.validate_on_submit():
			new_post = Post(post_form.group.data,
							current_user.UserID,
							post_form.title.data,
							post_form.body.data)
			
			db.session.add(new_post)
			db.session.commit()

			flash(u"Post created.", 'success')
			return redirect(url_for('index'))

		elif comment_form.validate_on_submit():
			new_comment = PostComment(comment_form.parent_post_id.data,
									current_user.UserID,
									comment_form.body.data)

			db.session.add(new_comment)
			db.session.commit()
			return redirect(url_for('index'))

	return render_template('index.html', 
							title='Home', 
							recent_posts=recent_posts,
							post_form=post_form,
							comment_form=comment_form,
							format_local_time=format_local_time
							)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_anonymous:
		form = LoginForm()
		if form.validate_on_submit():
			if check_credentials(form.username.data, form.password.data):
				user = User.query.filter(User.UserID == form.username.data).first()
				login_user(user, remember=form.remember_me.data)
				return redirect(url_for('index'))
			else:
				flash(u"Authentication failed, please check your username and password.", 'error')

		return render_template('login.html',
								title='Login',
								form=form)
	else:
		flash(u"You are already logged in.", 'message')
		return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'You have been logged out.', 'success')
	return redirect(url_for('login'))

@app.route('/forgot_password')
def forgot_password():
	return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
	if current_user.is_anonymous:
		form = CreateAccountForm()
		if form.validate_on_submit():
			if User.query.filter(User.UserID == form.user_id.data).count() > 0:
				flash(u"That User ID is already in use.", 'error')
				return redirect(url_for('create_account'))
			else:
				password_hash, salt = hash_password(form.password.data)
				password = "{}:{}".format(password_hash, salt)
				
				if form.year_level.data == 'None':
					year = None
				else:
					year = int(form.year_level.data)

				new_user = User(form.user_id.data, 
								form.user_type.data, 
								password, 
								year, 
								form.first_name.data, 
								form.last_name.data)
				db.session.add(new_user)
				db.session.commit()

				flash(u"User has been successfully created, please login.", 'success')
				return redirect(url_for('login'))

		return render_template('create_account.html',
								title='Create Account',
								form=form
								)
	else:
		flash(u"You are already logged in.", 'message')
		return redirect(url_for('index'))

@login_required
@app.route('/user/<UserID>')
def user(UserID):
	return redirect(url_for('index'))

@login_required
@app.route('/group/<GroupID>')
def group(GroupID):
	return redirect(url_for('index'))

@login_required
@app.route('/post/<PostID>')
def post(PostID):
	return redirect(url_for('index'))

@login_required
@app.route('/join_group/<GroupID>')
def join_group(GroupID):
	current_user.join_group(GroupID)

@login_required
@app.route('/delete/<Type>/<ID>')
def delete(Type, ID):
	if Type == 'Post':
		selected_post = Post.query.get(int(ID))
		if current_user.UserID == selected_post.UserID:
			for comment in selected_post.Comments:
				db.session.delete(comment)

			db.session.delete(selected_post)
			db.session.commit()

	if Type == 'PostComment':
		selected_comment = PostComment.query.get(int(ID))
		if current_user.UserID == selected_comment.AuthorID:
			db.session.delete(selected_comment)
			db.session.commit()

	return redirect(url_for('index'))


# Login Manager
@login_manager.user_loader
def load_user(UserID):
	return User.query.get(UserID)


# Prior to page load
@app.before_request
def before_request():
	"""Processing before each page is loaded, including setting user's LastSeen."""
	if current_user.is_authenticated:
		current_user.LastSeen = datetime.utcnow()
		db.session.add(current_user)
		db.session.commit()
