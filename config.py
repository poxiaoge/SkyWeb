import os

class Config:
    SECRET_KEY = os.environ.get('SECTER_KEY') or 'hard to guess string'

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    POST_PER_PAGE = 20

    WEB_ADMIN = '707886460@qq.com'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    MAIL_SUBJECT_PREFIX = '[help]'

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@localhost/myapp'

class ProductionConfig(Config):
    MAIL_SUBJECT_PREFIX = '[My_Web]'

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@localhost/myapp'

config = {
    'default' : DevelopmentConfig,
    'development' : DevelopmentConfig,
    'production' : ProductionConfig
}



