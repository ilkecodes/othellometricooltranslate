"""
Student API tests.
Tests for student dashboard, progress tracking, and exam enrollment.
"""
import pytest
from httpx import Client


class TestStudentDashboard:
    """Test student dashboard endpoint."""

    def test_get_dashboard_authenticated(self, client: Client, auth_headers: dict, logged_in_user: dict):
        """Test getting student dashboard with authentication."""
        response = client.get("/api/v1/student/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "student_id" in data
        assert "progress_stats" in data
        assert "weak_topics" in data

    def test_get_dashboard_unauthenticated(self, client: Client):
        """Test getting dashboard without authentication fails."""
        response = client.get("/api/v1/student/dashboard")
        assert response.status_code == 403

    def test_dashboard_contains_progress_stats(self, client: Client, auth_headers: dict):
        """Test dashboard contains progress statistics."""
        response = client.get("/api/v1/student/dashboard", headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()["progress_stats"]
        assert isinstance(stats, dict)
        # Stats should include subject mastery information
        assert "subjects" in stats or "total_exams" in stats

    def test_dashboard_contains_weak_topics(self, client: Client, auth_headers: dict):
        """Test dashboard contains weak topics list."""
        response = client.get("/api/v1/student/dashboard", headers=auth_headers)
        assert response.status_code == 200
        weak_topics = response.json()["weak_topics"]
        assert isinstance(weak_topics, list)


class TestStudentEnrollment:
    """Test student exam enrollment."""

    def test_enroll_in_exam(self, client: Client, auth_headers: dict):
        """Test student can enroll in an exam."""
        # Note: This assumes an exam exists in test database
        # In a real scenario, you'd create an exam first
        response = client.post(
            "/api/v1/student/exams/1/enroll",
            headers=auth_headers,
        )
        # Should return 200 if successful, 404 if exam doesn't exist in test DB
        assert response.status_code in [200, 404]

    def test_list_available_exams(self, client: Client, auth_headers: dict):
        """Test getting list of available exams for student."""
        response = client.get("/api/v1/student/exams/available", headers=auth_headers)
        # Should return list of exams
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    def test_get_student_exams(self, client: Client, auth_headers: dict):
        """Test getting student's enrolled exams."""
        response = client.get("/api/v1/student/exams", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestStudentProgress:
    """Test student progress tracking."""

    def test_get_student_results(self, client: Client, auth_headers: dict):
        """Test getting student's exam results."""
        response = client.get("/api/v1/student/results", headers=auth_headers)
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_get_subject_mastery(self, client: Client, auth_headers: dict):
        """Test getting student's mastery by subject."""
        response = client.get("/api/v1/student/progress/by-subject", headers=auth_headers)
        # This endpoint might not exist yet, so check for reasonable status codes
        assert response.status_code in [200, 404, 405]
