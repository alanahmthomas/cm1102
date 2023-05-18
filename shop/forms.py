from shop import app, db

from flask_login import current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, IntegerField, TextAreaField, DecimalField, SubmitField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed

from .models import User


class RegistrationForm(FlaskForm):
    fullname = StringField("Full name:", validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField("Email: *", validators=[DataRequired(), Email()])
    password = PasswordField("Password: *", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password: *", validators=[DataRequired(), EqualTo("password")])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Password:", validators=[DataRequired()])
    remember = BooleanField("Remember Me")

class CartForm(FlaskForm):
    product_id = IntegerField('Quantity:', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')

class CheckoutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    card_no = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16, message="The card number must be be 16 digits")])


    with app.app_context():
        db.create_all()