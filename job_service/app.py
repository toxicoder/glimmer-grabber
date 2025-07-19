from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from shared.database.database import get_db, engine
from shared.models.models import ProcessingJob, Card, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "Job Service"}
