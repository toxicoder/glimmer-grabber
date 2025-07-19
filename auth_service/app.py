# Placeholder app.py for auth_service
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from shared.database.database import get_db, engine
from shared.models.models import User, Base
from shared.schemas.schemas import UserCreate, User as UserSchema

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/")
def read_root():
    return {"Hello": "Auth Service"}
