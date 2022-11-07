import os
class Config(object):
    DEBUG =False
    TESTING = False
    SECRET_KEY ="neDLgvMuUjZQU4baleccjQ"
    DB_NAME = "production.db"
    DB_USERNAME = "root"
    DB_PASSWORD = "root"
    SESSION_COOKIE_SECURE = True
    ENV = "production"
    PDF_UPLOADS=os.path.join(os.getcwd(),"app","static","uploads_pdf")
    CLIENT_FOLDER=os.path.join(os.getcwd(),"app","static","client")
    USER_FILE = os.path.join(os.getcwd(),"app","static","users.pkl")



class ProductionConfig(Config):
    pass

class DeveolpmentConfig(Config):
    DEBUG =True

    DB_NAME = "dev.db"
    DB_USERNAME = "root"
    DB_PASSWORD = "root"

    SESSION_COOKIE_SECURE = False

    ENV="devolpment"

class TestingConfig(Config):
    TESTING =True

    DB_NAME = "test.db"
    DB_USERNAME = "root"
    DB_PASSWORD = "root"

    SESSION_COOKIE_SECURE = False

    ENV = "testing"
    

