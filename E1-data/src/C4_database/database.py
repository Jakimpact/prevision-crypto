from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from src.C4_database.models import Base
from src.settings import DatabaseSettings


def init_db(db_path=DatabaseSettings.DB_PATH, db_filename=DatabaseSettings.DB_FILENAME):
    """Initialise la base de données"""

    os.makedirs(db_path, exist_ok=True)
    engine = create_engine(f'sqlite:///{db_path}/{db_filename}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    return engine, Session