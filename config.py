import os


class Config:
    DEBUG = False
    SECRET_KEY = '1a0b329df51147t0va111335d2acbfd8'
    uri = os.environ.get("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
