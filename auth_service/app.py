# Placeholder app.py for auth_service
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Auth Service"}
