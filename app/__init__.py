#coding= utf-8
from flask import Flask,render_template
from flask_pagedown import PageDown
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import  Moment
from flask_login import LoginManager

#此处第1个config并不是MyWeb根目录下自己写的那个config，而是python 2.7库里的官方的config.py
from config import config

#如果写成bootstrap = Bootstrap(app)，那么就不需要下面的bootstrap.init_app(app)。但由于此时还没有app实例，因此就只能先空着了。
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main
    from .auth import auth
    from .api_1_0 import api
    app.register_blueprint(main,url_prefix='/main')
    app.register_blueprint(auth,url_prefix='/auth')
    app.register_blueprint(api,url_prefix='/api/v1.0')

    return app

