from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Unique key for user
    username = db.Column(db.String(20), unique=True, nullable=False)  # Unique name things, not null
    email = db.Column(db.String(120), unique=True, nullable=False)
    userAddress = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    posts = db.relationship('Post', backref="author", lazy=True)
    menus = db.relationship('Menu', backref="author", lazy=True)
    orders  = db.relationship('Orders', backref = "author", lazy = True)

    def getRole(self):
        return self.role

    def __repr__(self):
        return f"User('{self.username}', '{self.email}','{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique key for user
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique key for user
    location_name = db.Column(db.String(40), nullable = False)
    address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Place('{self.location_name}', '{self.address}')"
'''
class Restaurant(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Unique key for user
    username = db.Column(db.String(20), unique=True, nullable=False)  # Unique name things, not null
    email = db.Column(db.String(120), unique=True, nullable=False)
    userAddress = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    sales = db.Column(db.Float, nullable = False, default = 0)
    menus = db.relationship('Menu', backref="author", lazy=True)
    posts = db.relationship('Post', backref = "restaurant", lazy = True)
'''

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    org = db.Column(db.String(20), nullable=False)
    percentage = db.Column(db.Float, nullable=False, default=0)
    item1 = db.Column(db.String(20), nullable=False)
    item2 = db.Column(db.String(20), nullable=False)
    item3 = db.Column(db.String(20), nullable=False)
    item4 = db.Column(db.String(20), nullable=False)
    item5 = db.Column(db.String(20), nullable=False)
    price1 = db.Column(db.Float, nullable=False, default=0)
    price2 = db.Column(db.Float, nullable=False, default=0)
    price3 = db.Column(db.Float, nullable=False, default=0)
    price4 = db.Column(db.Float, nullable=False, default=0)
    price5 = db.Column(db.Float, nullable=False, default=0)
    num1 = db.Column(db.Integer, nullable = False, default = 0)
    num2 = db.Column(db.Integer, nullable=False, default=0)
    num3 = db.Column(db.Integer, nullable=False, default=0)
    num4 = db.Column(db.Integer, nullable=False, default=0)
    num5 = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False)
    userAddress = db.Column(db.String(120), nullable=False)
    qty1 = db.Column(db.Integer, nullable=False, default=0)
    qty2 = db.Column(db.Integer, nullable=False, default=0)
    qty3 = db.Column(db.Integer, nullable=False, default=0)
    qty4 = db.Column(db.Integer, nullable=False, default=0)
    qty5 = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)