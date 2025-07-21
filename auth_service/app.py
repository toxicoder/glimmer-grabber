# Placeholder app.py for auth_service
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from shared.database.database import get_db, engine
from shared.models.models import User, Base
from shared.schemas.schemas import UserCreate, User as UserSchema, Token, UserLogin
from . import utils, security
from .config import settings

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/api/v1/auth/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    db_user_by_email = db.query(User).filter(User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = utils.hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/v1/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = security.authenticate_user_by_email(db, email=user_credentials.email, password=user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: security.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = security.authenticate_user_by_username(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=UserSchema)
def read_users_me(current_user: User = Depends(security.get_current_active_user)) -> UserSchema:
    return current_user

@app.get("/")
def read_root() -> dict:
    return {"Hello": "Auth Service"}
