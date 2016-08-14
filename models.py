from flaskapp import db


# Table Definitions

class User(db.Model):
	"""Table defining Users"""
	UserID = db.column(db.String(10), primary_key=True, nullable=False)
	UserType = db.column(db.String(25), index=True, nullable=False)
	Password = db.column(db.String(97), nullable=False)
	Year = db.column(db.Integer, index=True)
	Name = db.column(db.String(200), index=True)
	MemberLinks = db.relationship('MemberLink', backref='LinkedUser', lazy='dynamic')
	Posts = db.relationship('Post', backref='Author', lazy='dynamic')
	Applications = db.relationship('Application', backref='Author', lazy='dynamic')

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return self.UserID

	def __repr__(self):
		return '<User ID {} of type {}>'.format(self.UserID, self.UserType)

class ServiceGroup(db.Model):
	"""Table defining Groups"""
	GroupID = db.column(db.Integer, primary_key=True, nullable=False)
	Name = db.column(db.String(100), index=True)
	MemberLinks = db.relationship('MemberLink', backref='LinkedGroup', lazy='dynamic')
	Posts = db.relationship('Post', backref='GroupPostedTo', lazy='dynamic')
	Applications = db.relationship('Application', backref='AppliedGroup', lazy='dynamic')

	def __repr__(self):
		return '<Group ID {} with name {}>'.format(self.GroupID, self.Name)

class MemberLink(db.Model):
	"""Table linking Users to Groups"""
	MemberLinkID = db.column(db.Integer, primary_key=True)
	UserID = db.Column(db.String(10), nullable=False, db.ForeignKey('User.UserID'))
	GroupID = db.Column(db.Integer, nullable=False, db.ForeignKey('ServiceGroup.GroupID'))
	ServiceHours = db.relationship('ServiceRecord', backref='ParentMemberLink', lazy='dynamic')

	def __repr__(self):
		return '<MemberLink ID {} linking UserID {} with GroupID {}>'.format(self.MemberLinkID, self.UserID, self.GroupID)

class ServiceRecord(db.Model):
	"""Table for recording service hours"""
	ServiceRecordID = db.column(db.Integer, primary_key=True)
	MemberLinkID = db.column(db.Integer, nullable=False, db.ForeignKey('MemberLink.MemberLinkID'))
	DateTime = db.column(db.DateTime, index=True)
	Hours = db.column(db.Interval)
	Status = db.column(db.String(20), index=True)
	Rostered = db.column(db.Boolean, index=True)
	Notes = db.column(db.String(1000))

	def __repr__(self):
		return '<ServiceRecord ID {} for MemberLinkID {} at {}>'.format(self.ServiceRecordID, self.MemberLinkID, self.DateTimePosted)

class Post(db.Model):
	"""Table for recording posts on group pages"""
	PostID = db.column(db.Integer, primary_key=True)
	GroupID = db.column(db.Integer, nullable=False, db.ForeignKey('ServiceGroup.GroupID'))
	UserID = db.column(db.String(10), nullable=False, db.ForeignKey('User.UserID'))
	DateTimePosted = db.column(db.DateTime, nullable=False, index=True)
	Title = db.column(db.String(100))
	Body = db.column(db.Body(10000))
	Comments = db.relationship('PostComment', backref='ParentPost', lazy='dynamic')

	def __repr__(self):
		return '<Post ID {} posted to GroupID {} by UserID {} at {}>'.format(self.PostID, self.GroupID, self.UserID, self.DateTimePosted)

class PostComment(db.Model):
	"""Table for recording comments on group posts"""
	PostCommentID = db.column(db.Integer, primary_key=True)
	ParentPostID = db.column(db.Integer, nullable=False, db.ForeignKey('Post.PostID'))
	AuthorID = db.column(db.Integer, nullable=False, db.ForeignKey('User.UserID'))
	DateTimeCommented = db.column(db.DateTime, nullable=False, index=True)
	Body = db.column(db.Body(1000))

	def __repr__(self):
		return '<PostComment ID {} by UserID {} on PostID {} at {}>'.format(self.PostCommentID, self.UserID, self.ParentPostID, self.DateTimeCommented)

class Application(db.Model):
	"""Table for recording applications to groups"""
	ApplicationID = db.column(db.Integer, primary_key=True)
	GroupID = db.column(db.Integer, nullable=False, db.ForeignKey('Service.Group.GroupID'))
	UserID = db.column(db.Integer, nullable=False, db.ForeignKey('User.UserID'))
	Parts = db.relationship('ApplicationPart', backref='ParentApplication', lazy='dynamic')

	def __repr__(self):
		return '<Application ID {} by UserID {} applying to GroupID {}>'.format(self.ApplicationID, self.GroupID, self.UserID)

class ApplicationPart(db.Model):
	"""Table for parts of applications to groups"""
	ApplicationPartID = db.column(db.Integer, primary_key=True)
	ParentApplicationID = db.column(db.Integer, nullable=False, db.ForeignKey('Application.ApplicationID'))
	Label = db.column(db.String(100), index=True)
	Content = db.column(db.String(5000))

	def __repr__(self):
		return '<ApplicationPart ID {} part of ApplicationID {} with label {}>'.format(self.ApplicationPartID, self.ParentApplicationID, self.Label)
