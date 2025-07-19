from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CardBase(BaseModel):
    card_number: str
    expiry_month: int
    expiry_year: int
    cvv: str

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int
    processing_job_id: int

    class Config:
        orm_mode = True

class ProcessingJobBase(BaseModel):
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class ProcessingJobCreate(ProcessingJobBase):
    pass

class ProcessingJob(ProcessingJobBase):
    id: int
    cards: List[Card] = []

    class Config:
        orm_mode = True
