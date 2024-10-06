from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config


# Replace these values with your actual database credentials
DATABASE_URL = f'postgresql://{config("DB_USER")}:{config("DB_PASSWORD")}@localhost/{config("DB_NAME")}'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()  # Assume you have your session set up
    try:
        yield db
    finally:
        db.close()

