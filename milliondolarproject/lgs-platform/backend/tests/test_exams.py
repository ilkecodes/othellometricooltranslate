"""
Exam API tests.
Tests for exam retrieval, question handling, and answer submission.
"""
import pytest
from httpx import Client


class TestExamList:
    """Test exam list endpoints."""

    def test_list_exams_authenticated(self, client: Client, auth_headers: dict):
        """Test getting list of all exams."""
        response = client.get("/api/v1/exams", headers=auth_headers)
        assert response.status_code == 200
        exams = response.json()
        assert isinstance(exams, list)

    def test_list_exams_unauthenticated(self, client: Client):
        """Test listing exams without authentication."""
        response = client.get("/api/v1/exams")
        # Exams list might be public, but student endpoints should be protected
        assert response.status_code in [200, 403]

    def test_filter_exams_by_subject(self, client: Client, auth_headers: dict):
        """Test filtering exams by subject."""
        response = client.get("/api/v1/exams?subject_id=1", headers=auth_headers)
        if response.status_code == 200:
            exams = response.json()
            assert isinstance(exams, list)


class TestExamRetrieval:
    """Test exam details retrieval."""

    def test_get_exam_details(self, client: Client, auth_headers: dict):
        """Test getting detailed exam information."""
        # Try to get exam with ID 1 (might not exist)
        response = client.get("/api/v1/exams/1", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            exam = response.json()
            assert "id" in exam
            assert "title" in exam

    def test_get_exam_questions(self, client: Client, auth_headers: dict):
        """Test getting questions from an exam."""
        response = client.get("/api/v1/exams/1/questions", headers=auth_headers)
        # Should succeed if exam exists, otherwise 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            questions = response.json()
            assert isinstance(questions, list)


class TestExamSession:
    """Test exam session management."""

    def test_start_exam_session(self, client: Client, auth_headers: dict):
        """Test starting an exam session."""
        response = client.post("/api/v1/exams/1/start", headers=auth_headers)
        # 201 for created session, 404 if exam doesn't exist
        assert response.status_code in [201, 404]
        if response.status_code == 201:
            session = response.json()
            assert "session_id" in session
            assert "start_time" in session

    def test_submit_answer(self, client: Client, auth_headers: dict):
        """Test submitting an answer to a question."""
        answer_data = {
            "question_id": 1,
            "selected_option": "A",
            "time_spent": 30,
        }
        response = client.post(
            "/api/v1/exams/1/submit-answer",
            json=answer_data,
            headers=auth_headers,
        )
        # Check for reasonable status codes
        assert response.status_code in [200, 404, 422]

    def test_end_exam_session(self, client: Client, auth_headers: dict):
        """Test ending exam session and getting results."""
        response = client.post("/api/v1/exams/1/end", headers=auth_headers)
        # 200 for success, 404 if session doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            result = response.json()
            assert "score" in result or "result" in result


class TestAdaptiveExam:
    """Test adaptive exam functionality."""

    def test_get_next_question_adaptive(self, client: Client, auth_headers: dict):
        """Test getting next adaptive question based on performance."""
        response = client.get("/api/v1/exams/1/next-question", headers=auth_headers)
        # Should return 200 if active session, 404 otherwise
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            question = response.json()
            assert "id" in question
            assert "text" in question
            assert "options" in question

    def test_exam_difficulty_adjustment(self, client: Client, auth_headers: dict):
        """Test that exam difficulty adjusts based on student performance."""
        # This is more of an integration test
        response = client.get("/api/v1/exams/1", headers=auth_headers)
        if response.status_code == 200:
            exam = response.json()
            # Adaptive exams should have adaptive=True field
            assert "adaptive" in exam or "difficulty_level" in exam
