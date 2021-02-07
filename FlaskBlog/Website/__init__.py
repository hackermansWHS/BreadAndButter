from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd78c756a9b3d38607f443ba43cf1ebf9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51GvzNSKS9hbYnczgfZhfCC7MzmeOZ9DGTgSpbDxhMx8AZdi5MDKQ2HvJeNcGn7R0Bca7r3KJR7Wp7OiqOV15oAR100fRK4zK2a'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51GvzNSKS9hbYnczgLAaJwodQ8AhsSPrCL8Wm8NQfUG7VZUJfTXlrY2B8hO5MrrSmm4j4zSQENpKgc0Pd3B4CfwAf00qAnmMDEy'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from flaskblog import routes