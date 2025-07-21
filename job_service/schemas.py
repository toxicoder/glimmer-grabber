from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CardBase(BaseModel):
    content: str

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int
    job_id: int

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
    s3_object_key: str
    cards: List[Card] = []

    class Config:
        orm_mode = True

from pydantic import validator
from typing import Any, Type

class JobCreationRequest(BaseModel):
    filename: str
    contentType: str

    @validator("contentType")
    def validate_content_type(cls: Type['JobCreationRequest'], value: str) -> str:
        if value not in ["image/jpeg", "image/png", "image/gif"]:
            raise ValueError("Unsupported content type")
        return value

class JobCreationResponse(BaseModel):
    jobId: int
    uploadUrl: str

class JobStatusResponse(BaseModel):
    status: str
    results: Optional[List[Card]] = None
