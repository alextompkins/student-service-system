from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, EqualTo, AnyOf


# Form Definitions
class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(message="Username required.")])
	password = PasswordField('password', validators=[InputRequired(message="Password required.")])
	remember_me = BooleanField('remember_me', default=False)

class CreateAccountForm(FlaskForm):
	user_id = StringField('user_id', validators=[InputRequired(message="Username required.")])
	password = PasswordField('password', validators=[InputRequired(message="Password required.")])
	reenter_password = PasswordField('reenter_password', validators=[EqualTo('password', message="Passwords must match.")])
	user_type = SelectField('User Type', 
		choices=[('Student', 'Student'), 
		('Teacher', 'Teacher'), 
		('Admin', 'Administrator')],
		validators=[AnyOf(values=['Student', 'Teacher', 'Admin'], message="Your user type was not one of the options.")])
	first_name = StringField('first_name', validators=[InputRequired(message="First name required.")])
	last_name = StringField('last_name', validators=[InputRequired(message="Last name required.")])
	year_level = SelectField('year_level', 
		choices=[('None', 'N/A'), 
		('9', '9'), 
		('10', '10'), 
		('11', '11'), 
		('12', '12'), 
		('13', '13'), 
		])

class CreatePostAnyGroupForm(FlaskForm):
	group = SelectField(u'group',)
	title = StringField('title', validators=[InputRequired(message="Your post needs a title.")])
	body = TextAreaField('body', validators=[InputRequired(message="Your post must say something.")])

class PostCommentForm(FlaskForm):
	parent_post_id = StringField('parent_post_id')
	body = StringField('body', validators=[InputRequired(message="Your comment must say something.")])