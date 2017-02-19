from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField,SubmitField,PasswordField,BooleanField,ValidationError,TextAreaField,SelectField
from wtforms.validators import Email,EqualTo,Regexp,InputRequired,Length
from ..models import User,Role

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



class EditProfileForm(Form):
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class AdminEditProfileForm(Form):
    nickname = StringField('Nickname',validators=[InputRequired(nickname_requred),Length(1,16,nickname_length),Regexp(nickname_reg_format,0,nickname_reg_msg)])
    email = StringField('Email',validators=[InputRequired(email_required),Email(email_invalid),Length(6,64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About Me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(AdminEditProfileForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data !=  self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exist!')

    def validate_nickname(self,field):
        if field.data != self.user.nickname and User.query.filter_by(nickname = field.data).first():
            raise ValidationError('Nickname already exist!')

class PostForm(Form):
    title = StringField('Title',validators=[InputRequired(),Length(1,64)])
    body = PageDownField('Post Body',validators=[InputRequired()],render_kw={"rows":"15"})
    submit = SubmitField('Submit')

class CommentForm(Form):
    body = StringField('YourComment',validators=[InputRequired()])
    submit = SubmitField('Submit')



