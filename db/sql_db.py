from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

SQL_ALCHEMY_URL = "sqlite:///sqlalchemy.sqlite.image.db"
engine = create_engine(f"mysql+mysqlconnector://{os.getenv('db_username')}:{os.getenv('db_password')}@{os.getenv('host')}:{os.getenv('port')}"
                       f"/imagedb", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
