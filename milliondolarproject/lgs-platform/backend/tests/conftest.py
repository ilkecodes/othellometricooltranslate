"""
Pytest configuration and fixtures for API testing.
"""
import os
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from httpx import Client

from app.main import app
from app.database import Base
from app.core.config import settings
from app.api.dependencies import get_db


# Use test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator:
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator:
    """Provide database session for tests."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Client:
    """Provide test client with overridden database."""
    app.dependency_overrides[get_db] = lambda: db
    with Client(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """Test user data for registration."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123!",
        "role": "student",
    }


@pytest.fixture
def test_teacher_data() -> dict:
    """Test teacher data for registration."""
    return {
        "email": "teacher@example.com",
        "full_name": "Test Teacher",
        "password": "teacherpass123!",
        "role": "teacher",
    }


@pytest.fixture
def registered_user(client: Client, test_user_data: dict) -> dict:
    """Register a test user and return user data with token."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    user_data = test_user_data.copy()
    user_data["user_id"] = response.json()["user"]["id"]
    return user_data


@pytest.fixture
def logged_in_user(client: Client, registered_user: dict) -> dict:
    """Register and login a test user, return with access token."""
    # Login to get token
    login_data = {
        "username": registered_user["email"],
        "password": registered_user["password"],
    }
    response = client.post(
        "/api/v1/auth/token",
        data=login_data,
    )
    assert response.status_code == 200
    token_data = response.json()
    registered_user["access_token"] = token_data["access_token"]
    registered_user["token_type"] = token_data["token_type"]
    return registered_user


@pytest.fixture
def auth_headers(logged_in_user: dict) -> dict:
    """Get authorization headers with bearer token."""
    return {
        "Authorization": f"{logged_in_user['token_type']} {logged_in_user['access_token']}"
    }
