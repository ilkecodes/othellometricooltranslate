"""
Authentication API tests.
Tests for user registration, login, and token validation.
"""
import pytest
from httpx import Client


class TestAuthRegister:
    """Test user registration endpoint."""

    def test_register_success(self, client: Client, test_user_data: dict):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["full_name"] == test_user_data["full_name"]
        assert data["user"]["role"] == "student"
        assert "id" in data["user"]

    def test_register_duplicate_email(self, client: Client, registered_user: dict, test_user_data: dict):
        """Test registration with duplicate email fails."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: Client):
        """Test registration with invalid email fails."""
        invalid_data = {
            "email": "not-an-email",
            "full_name": "Test User",
            "password": "testpass123!",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_missing_required_fields(self, client: Client):
        """Test registration with missing required fields fails."""
        response = client.post("/api/v1/auth/register", json={"email": "test@example.com"})
        assert response.status_code == 422

    def test_register_teacher(self, client: Client, test_teacher_data: dict):
        """Test successful teacher registration."""
        response = client.post("/api/v1/auth/register", json=test_teacher_data)
        assert response.status_code == 201
        assert response.json()["user"]["role"] == "teacher"


class TestAuthLogin:
    """Test user login endpoint."""

    def test_login_success(self, client: Client, registered_user: dict):
        """Test successful login returns access token."""
        login_data = {
            "username": registered_user["email"],
            "password": registered_user["password"],
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client: Client):
        """Test login with non-existent email fails."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword",
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 401

    def test_login_invalid_password(self, client: Client, registered_user: dict):
        """Test login with wrong password fails."""
        login_data = {
            "username": registered_user["email"],
            "password": "wrongpassword",
        }
        response = client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 401

    def test_login_missing_fields(self, client: Client):
        """Test login with missing fields fails."""
        response = client.post("/api/v1/auth/token", data={"username": "test@example.com"})
        assert response.status_code == 422


class TestTokenValidation:
    """Test token validation and authorization."""

    def test_me_endpoint_authenticated(self, client: Client, auth_headers: dict, logged_in_user: dict):
        """Test /me endpoint with valid token returns current user."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == logged_in_user["email"]
        assert data["full_name"] == logged_in_user["full_name"]

    def test_me_endpoint_unauthenticated(self, client: Client):
        """Test /me endpoint without token returns 401."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403

    def test_me_endpoint_invalid_token(self, client: Client):
        """Test /me endpoint with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_requires_auth(self, client: Client):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/v1/student/dashboard")
        assert response.status_code == 403
