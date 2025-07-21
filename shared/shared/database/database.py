from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.config import settings

if settings.TESTING:
    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
else:
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
