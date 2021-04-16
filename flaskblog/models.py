from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # backref like adding another column and when we have a post we can use this to get the author who made the post
    # lazy - SQLAlchemy will load the data as necessary in one go/post is not a column but just a query

    # how the obj is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
    # no content to speed up the loop

    def __init__(self, title, date_posted, content, user_id):
        self.title = title
        self.date_posted = date_posted
        self.content = content
        self.user_id = user_id