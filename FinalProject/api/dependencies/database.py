from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import conf
from urllib.parse import quote_plus
import os

# Use SQLite for development/testing, MySQL for production
# Set USE_MYSQL environment variable to "true" to use MySQL
USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() == "true"

if USE_MYSQL:
    # Use MySQL as required by project specifications
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{conf.db_user}:{quote_plus(conf.db_password)}@{conf.db_host}:{conf.db_port}/{conf.db_name}?charset=utf8mb4"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Use SQLite for development and testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./restaurant_app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
