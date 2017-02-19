from flask_wtf import Form
from wtforms import StringField,SubmitField,PasswordField,BooleanField,ValidationError
from wtforms.validators import Email,EqualTo,Regexp,InputRequired,Length
from ..models import User

nickname_requred='Nickname can not be null'
nickname_length='Nickname\'s length must between 1 and 16'
nickname_reg_format='^[a-zA-Z_][a-zA-Z0-9_]*$'
nickname_reg_msg='Nickname must start with letters,underscores and consist with only numbers,letters and underscores.'
password_required='Password can not be null!'
password_length='Password\'s length must between 6 and 24!'
remember_me_msg='Keep me logged in'
confirm_password_dismatch='Password must be match!'
confirm_password_required='Confirm password can not be null!'
email_required='Email can not be null!'
email_invalid='Invalid email!'

class NicknameLoginForm(Form):
    nickname = StringField('Nickname',validators=[InputRequired(nickname_requred),Length(1,16,nickname_length),Regexp(nickname_reg_format,0,nickname_reg_msg)])
    password = PasswordField('Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    remember_me = BooleanField(remember_me_msg)
    submit = SubmitField('Login')

class EmailLoginForm(Form):
    email = StringField('Email',validators=[InputRequired(email_required),Email(email_invalid),Length(6,64)])
    password = PasswordField('Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    remember_me = BooleanField(remember_me_msg)
    submit = SubmitField('Login')

class SigninForm(Form):
    nickname = StringField('Nickname',validators=[InputRequired(nickname_requred),Length(1,16,nickname_length),Regexp(nickname_reg_format,0,nickname_reg_msg)])
    email = StringField('Email',validators=[InputRequired(email_required),Email(email_invalid),Length(6,64)])
    password = PasswordField('Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    confirm_password = PasswordField('Confirm password',validators=[InputRequired(confirm_password_required),EqualTo('password',confirm_password_dismatch)])
    remember_me = BooleanField(remember_me_msg)
    submit = SubmitField('Signin')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered!')

    def validate_nickname(self,field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Nickname already registered!')

class ChangeEmailForm(Form):
    email = StringField('NewEmail',validators=[InputRequired(email_required),Email(email_invalid),Length(6,64)])
    password = PasswordField('Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    submit = SubmitField('ChangeEmail')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your new email is the same with the old one!')

class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    new_password = PasswordField('New Password',validators=[InputRequired(password_required),Length(6,24,password_length)])
    confirm_password = PasswordField('Confirm password',validators=[InputRequired(confirm_password_required),EqualTo('new_password',confirm_password_dismatch)])
    submit = SubmitField('ChangePassword')


class ResetPasswordForm(Form):
    email = StringField('Email',validators=[InputRequired(email_required),Email(email_invalid),Length(6,64)])
    submit = SubmitField('ResetPassword')

    def validate_email(self,field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Please input your account email or you can not reset your password!')


