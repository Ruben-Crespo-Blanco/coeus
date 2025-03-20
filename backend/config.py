import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Basic configuration class for Flask and SQLAlchemy.
    Adjust the database URI and SECRET_KEY for production.
    """
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///coeus.db")
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')

#
#
#