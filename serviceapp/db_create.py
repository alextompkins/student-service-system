from config import SQLALCHEMY_DATABASE_URI
from serviceapp import db

db.create_all()
print("Done creating all tables.")
