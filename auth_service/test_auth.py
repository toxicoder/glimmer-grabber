import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth_service.app import app, get_db
from shared.shared.models.models import Base, User


def override_get_db(dbsession):
    def _override_get_db():
        yield dbsession
    return _override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_get_db_fixture(dbsession):
    app.dependency_overrides[get_db] = override_get_db(dbsession)
    yield
    app.dependency_overrides.pop(get_db, None)


def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpassword", "email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_duplicate_user():
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpassword", "email": "test@example.com"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpassword", "email": "test@example.com"},
    )
    assert response.status_code == 400

def test_login():
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpassword", "email": "test@example.com"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
