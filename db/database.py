from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import get_env

engine = create_engine(
    get_env()["SQLALCHEMY_DATABASE_URL"],
    pool_size=40,
    max_overflow=50
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
