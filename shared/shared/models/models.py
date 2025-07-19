from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

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
