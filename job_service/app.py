# Placeholder app.py for job_service
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Job Service"}
