import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dummy-platform-secret-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DUMMY_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dummy_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
