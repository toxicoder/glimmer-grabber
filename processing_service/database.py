from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.shared.models.models import ProcessingJob, Card, Base
from shared.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
