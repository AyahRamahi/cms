from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """
    A class used with WTF to take user log in information

    Attributes
    ----------
    username : str
        the username of the user
    password : str
        the password of the user
    """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    """
    A class used with WTF to take user registration information

    Attributes
    ----------
    first_name : str
        the first name of the user
    last_name : str
        the last name of the user
    username : str
        the username of the user
    password : str
        the password of the user
    """

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Second Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])