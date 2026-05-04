import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# Add core-api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core-api")))

from main import app

from database import Base, get_db

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
from sqlalchemy import create_engine

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_and_login():
    # Register
    email = "test@example.com"
    password = "testpassword"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]

    # Check protected endpoint (get lists)
    response = client.get(
        "/api/v1/lists",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_es_error_fallback():
    # Mock ES URL to something invalid to test fallback/error handling
    # In main.py it's already using ELASTICSEARCH_URL env
    response = client.get("/api/v1/search?q=milk")
    # Even if ES fails, it should return an error structure as per main.py
    assert response.status_code == 200
    assert "items" in response.json()
