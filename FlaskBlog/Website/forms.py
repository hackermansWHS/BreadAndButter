from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    #role = StringField('Role (\"user\" or \"restaurant\")', validators = [DataRequired(),Length(min = 2, max = 20)])
    user = BooleanField('Normal User')
    restaurant = BooleanField('Restaurant')
    username = StringField('Username', validators = [DataRequired(),Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    userAddress = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators = [ DataRequired()])
    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired()])
    password = PasswordField('Password', validators = [ DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(),Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')

class RestaurantForm(FlaskForm):
    username = StringField('Restaurant Name', validators = [DataRequired(),Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    userAddress = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators = [ DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
class MenuForm(FlaskForm):
    org = StringField('Supported Charity', validators=[DataRequired()])
    percentage = StringField('Percentage of Proceeds to Charity', validators=[DataRequired()])
    item1 = StringField('First Item', validators=[DataRequired()])
    item2 = StringField('Second Item', validators=[DataRequired()])
    item3 = StringField('Third Item', validators=[DataRequired()])
    item4 = StringField('Fourth Item', validators=[DataRequired()])
    item5 = StringField('Fifth Item', validators=[DataRequired()])
    price1 = StringField('Price of First Item', validators=[DataRequired()])
    price2 = StringField('Price of Second Item', validators=[DataRequired()])
    price3 = StringField('Price of Third Item', validators=[DataRequired()])
    price4 = StringField('Price of Fourth Item', validators=[DataRequired()])
    price5 = StringField('Price of Fifth Item', validators=[DataRequired()])
    submit = SubmitField('Create')

class OrderForm(FlaskForm):
    username =  StringField('Username', validators=[DataRequired()])
    userAddress = StringField('User Address', validators=[DataRequired()])
    qty1 = StringField('', validators=[DataRequired()])
    qty2 = StringField('', validators=[DataRequired()])
    qty3 = StringField('', validators=[DataRequired()])
    qty4 = StringField('', validators=[DataRequired()])
    qty5 = StringField('', validators=[DataRequired()])
    submit = SubmitField('Order')

class MapForm(FlaskForm):
    restaurant = SubmitField('Show Restaurants')
    events = SubmitField('Show Events')