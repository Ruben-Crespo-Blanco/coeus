import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    """
    Basic configuration class for Flask and SQLAlchemy.
    Adjust the database URI and SECRET_KEY for production.
    """
    # Example uses a local SQLite file named 'example.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///coeus.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')