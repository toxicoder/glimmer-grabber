# Placeholder app.py for job_service
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/jobdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    status = Column(String, index=True)

    cards = relationship("Card", back_populates="job")

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, status='{self.status}')>"

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    content = Column(String)

    job = relationship("ProcessingJob", back_populates="cards")

    def __repr__(self):
        return f"<Card(id={self.id})>"

@app.get("/")
def read_root():
    return {"Hello": "Job Service"}
