from serviceapp import db
from datetime import datetime


# Table Definitions
class User(db.Model):
	"""Table defining Users"""
	__tablename__ = "User"

	UserID = db.Column(db.String(10), primary_key=True, nullable=False)
	UserType = db.Column(db.String(25), index=True, nullable=False)
	Password = db.Column(db.String(97), nullable=False)
	Year = db.Column(db.Integer, index=True)
	FirstName = db.Column(db.String(100), index=True)
	LastName = db.Column(db.String(100), index=True)
	LastSeen = db.Column(db.DateTime)
	MemberLinks = db.relationship('MemberLink', backref='Member', lazy='dynamic')
	Posts = db.relationship('Post', backref='Author', lazy='dynamic')
	Comments = db.relationship('PostComment', backref='Author', lazy='dynamic')
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

	def is_member_of(self, group):
		for link in self.MemberLinks:
			if link.UserID == self.UserID and link.GroupID == group.GroupID:
				return True
		return False

	def get_groups(self):
		return tuple(ServiceGroup.query.filter(ServiceGroup.GroupID == link.GroupID).first() for link in self.MemberLinks)

	def join_group(self, group, MemberRole=None):
		if MemberLink.query.filter(MemberLink.UserID == self.UserID, MemberLink.GroupID == group.GroupID).count() > 0:
			raise ValueError("MemberLink between User {} and Group {} already exists".format(self.UserID, group.GroupID))
		else:
			link = MemberLink(self.UserID, group.GroupID, MemberRole)
			db.session.add(link)
			db.session.commit()

	def __init__(self, UserID, UserType, Password, Year, FirstName, LastName):
		self.UserID = UserID
		self.UserType = UserType
		self.Password = Password
		self.Year = Year
		self.FirstName = FirstName
		self.LastName = LastName
		self.LastSeen = datetime.utcnow()

	def __repr__(self):
		return '<User ID {} of type {}>'.format(self.UserID, self.UserType)

class ServiceGroup(db.Model):
	"""Table defining Groups"""
	__tablename__ = "ServiceGroup"

	GroupID = db.Column(db.Integer, primary_key=True, nullable=False)
	Name = db.Column(db.String(100), index=True)
	MemberLinks = db.relationship('MemberLink', backref='LinkedGroup', lazy='dynamic')
	Posts = db.relationship('Post', backref='GroupPostedTo', lazy='dynamic')
	Applications = db.relationship('Application', backref='AppliedGroup', lazy='dynamic')

	def get_members(self):
		return tuple(User.query.filter(User.UserID == link.UserID).first() for link in self.MemberLinks)

	def __init__(self, Name):
		self.Name = Name

	def __repr__(self):
		return '<Group ID {} with name {}>'.format(self.GroupID, self.Name)

class MemberLink(db.Model):
	"""Table linking Users to Groups"""
	__tablename__ = "MemberLink"

	MemberLinkID = db.Column(db.Integer, primary_key=True)
	UserID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	GroupID = db.Column(db.Integer, db.ForeignKey('ServiceGroup.GroupID'), nullable=False)
	MemberRole = db.Column(db.String(30), index=True)
	ServiceHours = db.relationship('ServiceRecord', backref='ParentMemberLink', lazy='dynamic')

	def __init__(self,  UserID, GroupID, MemberRole=None):
		self.UserID = UserID
		self.GroupID = GroupID
		self.MemberRole = MemberRole

	def __repr__(self):
		return '<MemberLink ID {} linking UserID {} with GroupID {}>'.format(self.MemberLinkID, self.UserID, self.GroupID)

class ServiceRecord(db.Model):
	"""Table defining records of school service"""
	__tablename__ = "ServiceRecord"

	"""Table for recording service hours"""
	ServiceRecordID = db.Column(db.Integer, primary_key=True)
	MemberLinkID = db.Column(db.Integer, db.ForeignKey('MemberLink.MemberLinkID'), nullable=False)
	DateTime = db.Column(db.DateTime, index=True)
	Hours = db.Column(db.Interval)
	Status = db.Column(db.String(20), index=True)
	Rostered = db.Column(db.Boolean, index=True)
	Notes = db.Column(db.String(1000))

	def __init__(self, MemberLinkID, DateTime, Hours, Status, Rostered, Notes):
		self.MemberLinkID = MemberLinkID
		self.DateTime = DateTime
		self.Hours = Hours
		self.Status = Status
		self.Rostered = Rostered
		self.Notes = Notes

	def __repr__(self):
		return '<ServiceRecord ID {} for MemberLinkID {} at {}>'.format(self.ServiceRecordID, self.MemberLinkID, self.DateTimePosted)

class Post(db.Model):
	"""Table for recording posts on group pages"""
	__tablename__ = "Post"

	PostID = db.Column(db.Integer, primary_key=True)
	GroupID = db.Column(db.Integer, db.ForeignKey('ServiceGroup.GroupID'), nullable=False)
	UserID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	DateTimePosted = db.Column(db.DateTime, nullable=False, index=True)
	Title = db.Column(db.String(100))
	Body = db.Column(db.String(10000))
	Comments = db.relationship('PostComment', backref='ParentPost', lazy='dynamic')

	def get_body_lines(self):
		return self.Body.split('\n')

	def __init__(self, GroupID, UserID, Title, Body):
		self.GroupID = GroupID
		self.UserID = UserID
		self.DateTimePosted = datetime.utcnow()
		self.Title = Title
		self.Body = Body

	def __repr__(self):
		return '<Post ID {} posted to GroupID {} by UserID {} at {}>'.format(self.PostID, self.GroupID, self.UserID, self.DateTimePosted)

class PostComment(db.Model):
	"""Table for recording comments on group posts"""
	__tablename__ = "PostComment"

	PostCommentID = db.Column(db.Integer, primary_key=True)
	ParentPostID = db.Column(db.Integer, db.ForeignKey('Post.PostID'), nullable=False)
	AuthorID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	DateTimeCommented = db.Column(db.DateTime, nullable=False, index=True)
	Body = db.Column(db.String(1000))

	def __init__(self, ParentPostID, AuthorID, Body):
		self.ParentPostID = ParentPostID
		self.AuthorID = AuthorID
		self.DateTimeCommented = datetime.utcnow()
		self.Body = Body

	def __repr__(self):
		return '<PostComment ID {} by UserID {} on PostID {} at {}>'.format(self.PostCommentID, self.UserID, self.ParentPostID, self.DateTimeCommented)

class Application(db.Model):
	"""Table for recording applications to groups"""
	__tablename__ = "Application"

	ApplicationID = db.Column(db.Integer, primary_key=True)
	GroupID = db.Column(db.Integer, db.ForeignKey('ServiceGroup.GroupID'), nullable=False)
	UserID = db.Column(db.String(10), db.ForeignKey('User.UserID'), nullable=False)
	Parts = db.relationship('ApplicationPart', backref='ParentApplication', lazy='dynamic')

	def __repr__(self):
		return '<Application ID {} by UserID {} applying to GroupID {}>'.format(self.ApplicationID, self.GroupID, self.UserID)

class ApplicationPart(db.Model):
	"""Table for parts of applications to groups"""
	__tablename__ = "ApplicationPart"

	ApplicationPartID = db.Column(db.Integer, primary_key=True)
	ParentApplicationID = db.Column(db.Integer, db.ForeignKey('Application.ApplicationID'), nullable=False)
	Label = db.Column(db.String(100), index=True)
	Content = db.Column(db.String(5000))

	def __repr__(self):
		return '<ApplicationPart ID {} part of ApplicationID {} with label {}>'.format(self.ApplicationPartID, self.ParentApplicationID, self.Label)
