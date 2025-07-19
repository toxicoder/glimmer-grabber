import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from job_service.app import app, get_db
from shared.models.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_job():
    response = client.post(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer 1"},
        json={"filename": "test.txt", "contentType": "text/plain"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "jobId" in data
    assert "uploadUrl" in data


def test_create_job_unauthorized():
    response = client.post(
        "/api/v1/jobs",
        json={"filename": "test.txt", "contentType": "text/plain"},
    )
    assert response.status_code == 401
