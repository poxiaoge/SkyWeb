from flask import render_template,redirect,request,url_for,flash,session,current_app
from .forms import *
from ..models import User,Permission
from flask_login import login_user,login_required,logout_user,current_user
from . import auth
from .. import db
from ..email import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import random
from datetime import datetime
from ..decorators import permission_required,admin_required

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5]!= 'auth.' and request.endpoint !='static':
        return redirect(url_for('auth.unconfirmed'))

# @auth.before_app_first_request
# def before_first_request():
#     current_user.update_last_screen()



@auth.route('/')
def index():
    return redirect(url_for('main.index'))

@auth.route('/login',methods=['GET','POST'])
def login():
    form = NicknameLoginForm()
    login_with_email=False
    if form.validate_on_submit():
        user=User.query.filter_by(nickname=form.nickname.data).first()
        if user is  None:
            flash('Invalid username!')
            form.nickname.data = ""
            return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)
        elif user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid password!')
            form.password.data = ""
            return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)
    return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)

@auth.route('/login-with-email',methods=['GET','POST'])
def login_with_email():
    form = EmailLoginForm()
    login_with_email=True
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is  None:
            flash('Invalid email!')
            form.email.data = ""
            return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)
        elif user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect( request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid password!')
            form.password.data = ""
            return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)
    return render_template('login.html',header='Login',form=form,login_with_email=login_with_email)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have log out!')
    return redirect(url_for('auth.login'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = SigninForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data,password=form.password.data,email=form.email.data,member_since = datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_token()
        login_user(user)
        send_email(form.email.data,'confirm','email/confirm',name=form.nickname.data,token=token)
        flash('An email has been sent to your email')
        return redirect(url_for('auth.unconfirmed'))
    return render_template('forms_base.html',header='Register',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('Do not repeat to confirm your email!')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have successfully confirmed your email!Enjoy!')
        return render_template('info_base.html',header='Email Confirm',info='Successfully confirmed your email!')
    else:
        flash('The confirmation link is invalid or has expired')
        return render_template('info_base.html',header='Email Confirm',info='Email confirm error!')



@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('info_base.html',header='Unconfirmed',info='Please check your register emailbox and confirm your email!')

@auth.route('/resend-confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirm_token()
    send_email(current_user.email,'Confirm','email/confirm',name=current_user.nickname,token=token)
    flash('A new confirmation email has been sent by email!')
    return render_template('info_base.html',header='Resend Confirmation',info='Please check your register emailbox and confirm your email!')


@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            flash('Wrong password!')
            return render_template('forms_base.html',header='Change Email',form=form)
        email_dict={'old_email':current_user.email,'new_email':form.email.data}
        token = current_user.generate_change_email_token(dump_dict=email_dict)
        send_email(current_user.email,'old_email_confirm','email/old_email_confirm',name=current_user.nickname,token=token)
        flash('A new confirmation has been sent to your old email!')
        return render_template('info_base.html',header='Change Email',info='Please check your old email!')
    return render_template('forms_base.html',header='Change Email',form = form)

@auth.route('/old-email-confirm/<token>')
@login_required
def old_email_confirm(token):
    s = Serializer(current_app.config.get('SECRET_KEY'))
    try:
        data=s.loads(token)
    except:
        return render_template('info_base.html',header='Old Email Confirm',info='Confirm Error!')
    if data.get('old_email') != current_user.email:
        return render_template('info_base.html',header='Old Email Confirm',info='Confirm Error!')
    new = data.get('new_email')
    current_user.email = new
    current_user.confirmed = False
    db.session.add(current_user)
    db.session.commit()
    # email_dict = {'confirm':new}
    # token = current_user.generate_change_email_token(dump_dict=email_dict)
    token = current_user.generate_confirm_token()
    send_email(new,'new_email_confirm','email/confirm',name=current_user.nickname,token=token)
    flash('A new confirmation has been sent to your new email!')
    return render_template('info_base.html',header='Old Email Confirm',info='Old email confirm Success!Please check your new email!')

# @auth.route('/new-email-confirm/<token>')
# @login_required
# def new_email_confirm(token):
#     s = Serializer(current_app.config.get('SECRET_KEY'))
#     try:
#         data=s.loads(token)
#     except:
#         return render_template('info_base.html',header='New Email Confirm',info='Confirm Error!')
#     if data.get('new_email') != current_user.email:
#         return render_template('info_base.html',header='New Email Confirm',info='Confirm Error!')
#     current_user.confirmed = True
#     flash('New email confirm successfully!')
#     return redirect(url_for('main.index'))

@auth.route('/change-password',methods=['POST','GET'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash('Wrong old password!')
            form.old_password.data=""
            return render_template('forms_base.html',header='Change Password',form = form)
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        logout_user()
        flash('password change successfully!')
        return redirect(url_for('auth.login'))
    return render_template('forms_base.html',header='Change Password',form=form)

@auth.route('/reset-password',methods=['POST','GET'])
def reset_password():
    if current_user.is_authenticated:
        logout_user()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        random_pass = random.randint(10000000,99999999)
        dump_dict = {'new_password':str(random_pass),'email':user.email}
        token = user.generate_change_email_token(dump_dict=dump_dict)
        send_email(form.email.data,'Reset Password','email/reset_password',name = user.nickname,token=token,password=random_pass)
        flash('A new password has been sent to your email!Please check your email and activate the new password! ')
        return redirect(url_for('auth.login'))
    return  render_template('forms_base.html',header='Reset Password',form = form)

@auth.route('/active-password/<token>')
def active_password(token):
    s = Serializer(current_app.config.get('SECRET_KEY'))
    try:
        data=s.loads(token)
    except:
        return render_template('info_base.html',header='Active password',info='Activate password Error!')
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    user.password = data.get('new_password')
    db.session.add(user)
    db.session.commit()
    flash('New password activate successfully!')
    return redirect(url_for('auth.login'))