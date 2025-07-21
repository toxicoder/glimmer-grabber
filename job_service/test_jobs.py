import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from moto import mock_aws
import boto3
from unittest.mock import patch
import os

from job_service.app import app, get_db
from shared.shared.models.models import Base

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


@pytest.fixture(autouse=True)
def mock_s3_bucket():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        yield


@patch("pika.BlockingConnection")
def test_create_job(mock_pika):
    response = client.post(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer 1"},
        json={"filename": "test.txt", "contentType": "image/jpeg"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "jobId" in data
    assert "uploadUrl" in data


@patch("pika.BlockingConnection")
def test_create_job_unauthorized(mock_pika):
    response = client.post(
        "/api/v1/jobs",
        json={"filename": "test.txt", "contentType": "image/jpeg"},
    )
    assert response.status_code == 401


def test_read_jobs():
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch("pika.BlockingConnection")
def test_read_job(mock_pika):
    # First, create a job to read
    response = client.post(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer 1"},
        json={"filename": "test.txt", "contentType": "image/jpeg"},
    )
    job_id = response.json()["jobId"]

    response = client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": "Bearer 1"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"


def test_read_job_not_found():
    response = client.get("/api/v1/jobs/999", headers={"Authorization": "Bearer 1"})
    assert response.status_code == 404


@patch("pika.BlockingConnection")
def test_update_job(mock_pika):
    # First, create a job to update
    response = client.post(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer 1"},
        json={"filename": "test.txt", "contentType": "image/jpeg"},
    )
    job_id = response.json()["jobId"]

    response = client.put(f"/jobs/{job_id}", json={"status": "COMPLETED"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"


@patch("pika.BlockingConnection")
def test_delete_job(mock_pika):
    # First, create a job to delete
    response = client.post(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer 1"},
        json={"filename": "test.txt", "contentType": "image/jpeg"},
    )
    job_id = response.json()["jobId"]

    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id

    # Verify the job is deleted
    response = client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": "Bearer 1"})
    assert response.status_code == 404


def test_get_collection():
    response = client.get("/api/v1/collections", headers={"Authorization": "Bearer 1"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
