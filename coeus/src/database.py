from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# Create the SQLAlchemy engine
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency function for getting DB session in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Note: For SQLite in-memory or file-based usage, you need check_same_thread=False if you use it in multiple threads, which FastAPI may do. For production, you’d likely use PostgreSQL or MySQL, in which case you remove that connect argument.