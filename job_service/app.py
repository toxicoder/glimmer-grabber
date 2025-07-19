from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared.database.database import get_db, engine
from shared.models.models import ProcessingJob, Card, Base
from . import schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/jobs/", response_model=schemas.ProcessingJob)
def create_job(job: schemas.ProcessingJobCreate, db: Session = Depends(get_db)):
    db_job = ProcessingJob(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=List[schemas.ProcessingJob])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(ProcessingJob).offset(skip).limit(limit).all()
    return jobs

@app.get("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.put("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def update_job(job_id: int, job: schemas.ProcessingJobCreate, db: Session = Depends(get_db)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    for var, value in vars(job).items():
        setattr(db_job, var, value) if value else None
    db.commit()
    db.refresh(db_job)
    return db_job

@app.delete("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return db_job
