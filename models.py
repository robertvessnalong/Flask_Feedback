from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
    db.create_all()

class User(db.Model):

    __tablename__ = 'users'
    
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first, last):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, 
                   password=hashed_utf8,
                   email=email, 
                   first_name=first, 
                   last_name=last)

    @classmethod
    def authenticate(cls, username, password):
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Feedback(db.Model):

    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username') )

    user = db.relationship('User', backref=backref("feedback", cascade="all,delete"))