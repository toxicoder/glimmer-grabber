import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models.models import ProcessingJob, Card, Base

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres/database")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
