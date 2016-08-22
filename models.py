from serviceapp import db


# Table Definitions

class User(db.Model):
	"""Table defining Users"""
	UserID = db.Column(db.String(10), primary_key=True, nullable=False)
	UserType = db.Column(db.String(25), index=True, nullable=False)
	Password = db.Column(db.String(97), nullable=False)
	Year = db.Column(db.Integer, index=True)
	Name = db.Column(db.String(200), index=True)
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
	GroupID = db.Column(db.Integer, primary_key=True, nullable=False)
	Name = db.Column(db.String(100), index=True)
	MemberLinks = db.relationship('MemberLink', backref='LinkedGroup', lazy='dynamic')
	Posts = db.relationship('Post', backref='GroupPostedTo', lazy='dynamic')
	Applications = db.relationship('Application', backref='AppliedGroup', lazy='dynamic')

	def __repr__(self):
		return '<Group ID {} with name {}>'.format(self.GroupID, self.Name)

class MemberLink(db.Model):
	"""Table linking Users to Groups"""
	MemberLinkID = db.Column(db.Integer, primary_key=True)
	UserID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	GroupID = db.Column(db.Integer, db.ForeignKey('ServiceGroup.GroupID'), nullable=False)
	ServiceHours = db.relationship('ServiceRecord', backref='ParentMemberLink', lazy='dynamic')

	def __repr__(self):
		return '<MemberLink ID {} linking UserID {} with GroupID {}>'.format(self.MemberLinkID, self.UserID, self.GroupID)

class ServiceRecord(db.Model):
	"""Table for recording service hours"""
	ServiceRecordID = db.Column(db.Integer, primary_key=True)
	MemberLinkID = db.Column(db.Integer, db.ForeignKey('MemberLink.MemberLinkID'), nullable=False)
	DateTime = db.Column(db.DateTime, index=True)
	Hours = db.Column(db.Interval)
	Status = db.Column(db.String(20), index=True)
	Rostered = db.Column(db.Boolean, index=True)
	Notes = db.Column(db.String(1000))

	def __repr__(self):
		return '<ServiceRecord ID {} for MemberLinkID {} at {}>'.format(self.ServiceRecordID, self.MemberLinkID, self.DateTimePosted)

class Post(db.Model):
	"""Table for recording posts on group pages"""
	PostID = db.Column(db.Integer, primary_key=True)
	GroupID = db.Column(db.Integer, db.ForeignKey('ServiceGroup.GroupID'), nullable=False)
	UserID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	DateTimePosted = db.Column(db.DateTime, nullable=False, index=True)
	Title = db.Column(db.String(100))
	Body = db.Column(db.String(10000))
	Comments = db.relationship('PostComment', backref='ParentPost', lazy='dynamic')

	def __repr__(self):
		return '<Post ID {} posted to GroupID {} by UserID {} at {}>'.format(self.PostID, self.GroupID, self.UserID, self.DateTimePosted)

class PostComment(db.Model):
	"""Table for recording comments on group posts"""
	PostCommentID = db.Column(db.Integer, primary_key=True)
	ParentPostID = db.Column(db.Integer, db.ForeignKey('Post.PostID'), nullable=False)
	AuthorID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
	DateTimeCommented = db.Column(db.DateTime, nullable=False, index=True)
	Body = db.Column(db.String(1000))

	def __repr__(self):
		return '<PostComment ID {} by UserID {} on PostID {} at {}>'.format(self.PostCommentID, self.UserID, self.ParentPostID, self.DateTimeCommented)

class Application(db.Model):
	"""Table for recording applications to groups"""
	ApplicationID = db.Column(db.Integer, primary_key=True)
	GroupID = db.Column(db.Integer, db.ForeignKey('Service.Group.GroupID'), nullable=False)
	UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
	Parts = db.relationship('ApplicationPart', backref='ParentApplication', lazy='dynamic')

	def __repr__(self):
		return '<Application ID {} by UserID {} applying to GroupID {}>'.format(self.ApplicationID, self.GroupID, self.UserID)

class ApplicationPart(db.Model):
	"""Table for parts of applications to groups"""
	ApplicationPartID = db.Column(db.Integer, primary_key=True)
	ParentApplicationID = db.Column(db.Integer, db.ForeignKey('Application.ApplicationID'), nullable=False)
	Label = db.Column(db.String(100), index=True)
	Content = db.Column(db.String(5000))

	def __repr__(self):
		return '<ApplicationPart ID {} part of ApplicationID {} with label {}>'.format(self.ApplicationPartID, self.ParentApplicationID, self.Label)
