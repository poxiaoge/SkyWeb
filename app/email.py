from . import mail
from flask_mail import Message
from threading import Thread
from flask import current_app,render_template

def send_asyc_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(dst,subject,template,**kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=app.config.get('MAIL_SUBJECT_PREFIX')+subject,recipients=[dst],sender=app.config.get('MAIL_USERNAME'))
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    # print "send mail:"+dst+":"+current_app.config['MAIL_USERNAME']
    mail_thread = Thread(target=send_asyc_email,args=[app,msg])
    mail_thread.start()
    return mail_thread
