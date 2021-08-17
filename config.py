import os


class Config:
    DEBUG = False
    SECRET_KEY = '1a0b329df51147t0va111335d2acbfd8'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False