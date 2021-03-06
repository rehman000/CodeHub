from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer              # For email Reset JSON token! 
from flask import current_app                                                       # I need to import this instead of app, because app is now in create_app(), so it's out of scope!
from app import db, login_manager, ma                                             # Resolves issue with circular imports! Login manager is a flask-extension
from flask_login import UserMixin                                                   # Really useful extension for authentication, and session management, accepts user_id 
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema

@login_manager.user_loader 
def laod_user(user_id):
    return User.query.get(int(user_id))                                             # getter function that helps get the user_id


'''

class Groups(db.Model):
    id = superkey
    name =  string not nullable
    image_file = not nullable
    users = foreign key into the table User
    status = relationship('Post', backref='author', lazy=True) # This has to be many to many relationship! 

'''

# START of Groups changes

# Creates Groups table in db
class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(20), nullable=False)
    group_desc = db.Column(db.Text, nullable=False)
    visible_posts = db.Column(db.Boolean, nullable=False)
    visible_members = db.Column(db.Boolean, nullable=False)
    visible_eval = db.Column(db.Boolean, nullable=False)
    visible_warn = db.Column(db.Boolean, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Groups('{self.group_id}')"


class GroupMembers(db.Model):
    group_id = db.Column(db.Integer, db.ForeignKey(
        'groups.group_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f"GroupMembers('{self.group_id}')"

class GroupSchema(ma.SQLAlchemySchema):
    class Meta:
        fields = ('group_id', 'group_name', 'group_desc',
                  'visible_posts', 'visible_members', 'visible_eval', 'visible_warn', 'rating')

class GroupMemSchema(ma.SQLAlchemySchema):
    class Meta:
        fields = ('group_id', 'user_id')


# Added poll features in here for convenience
class Poll(db.Model):
    poll_id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey(
        'groups.group_id'), nullable=False)
    
    def __repr__(self):
        return f"Poll('{self.desc}', '{self.group_id}')"
        
class PollOptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(100), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey(
        'poll.poll_id'), nullable=False)
    votes = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"PollOptions('{self.option}', '{self.poll_id}', '{self.votes}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)                                    # Primary Key
    username = db.Column(db.String(20), unique=True, nullable=False)                # Each User will have a username, with a max(20) characters, it must be unique, and Null is not allowed!
    email = db.Column(db.String(120), unique=True, nullable=False)                  # Each User will have an email, with a max(120) characters, it must be unique, and Null is not allowed!
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')    # Each User will have a defualt profile Image, so uniqueness does not apply, since Null is not allowed! 
    password = db.Column(db.String(60), nullable=False)                             # Each User will have passwords, with a max(60) characters, uniqueness does not apply, and Null is not allowed!
    posts = db.relationship('Post', backref='author', lazy=True)                    # This is linked to Posts, Lazy Evaluation is set to: True

    reputation = db.Column(db.Integer, nullable=False, default=10)                  # This has a default value of 10
    profanity = db.Column(db.Boolean, unique=False, default=False)                  # This had a default value of 0
    chance = db.Column(db.Boolean, nullable=False, default=True)                    # This has a default value of True
    blacklisted = db.Column(db.Boolean, unique=False, default=False)                # This has a default value of False
    compliments=db.Column(db.Integer, unique=False, default=0)                      # This has a default value of 0


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')                        # s.dumps returns a payload! decode 'utf-8' makes sure were returning a string and not bytes 

    @staticmethod                                                                   # This method needs to be static so that it cannot reference self, only the token can be passed in! 
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)                                              # So if everything goes smoothly, and no exceptions go off, return the user in the database with user_id.

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)                                    # Primary Key
    title = db.Column(db.String(100), nullable=False)                               # Each Post will have a title, with a max(100) characters, uniqueness does not apply, and Null is not allowed!
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   # Each Post will have a date_posted, with DateTime set to utcnow, current time, and Null is not allowed!
    content = db.Column(db.Text, nullable=False)                                    # Each Post will have a content with no character limit, and Null is not allowed!
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)       # This is using the user id as a ForeignKey, each post must have an Author, so Null is not allowed!
    rating = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
