"""
Curriculum API tests.
Tests for curriculum structure (subjects, units, topics, learning outcomes).
"""
import pytest
from httpx import Client


class TestSubjects:
    """Test subject endpoints."""

    def test_list_subjects(self, client: Client, auth_headers: dict):
        """Test getting list of all subjects."""
        response = client.get("/api/v1/curriculum/subjects", headers=auth_headers)
        assert response.status_code == 200
        subjects = response.json()
        assert isinstance(subjects, list)

    def test_get_subject_details(self, client: Client, auth_headers: dict):
        """Test getting detailed subject information."""
        response = client.get("/api/v1/curriculum/subjects/1", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            subject = response.json()
            assert "id" in subject
            assert "name" in subject
            assert "units" in subject

    def test_list_subject_units(self, client: Client, auth_headers: dict):
        """Test getting units within a subject."""
        response = client.get("/api/v1/curriculum/subjects/1/units", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            units = response.json()
            assert isinstance(units, list)


class TestUnits:
    """Test unit endpoints."""

    def test_list_all_units(self, client: Client, auth_headers: dict):
        """Test getting list of all units."""
        response = client.get("/api/v1/curriculum/units", headers=auth_headers)
        assert response.status_code == 200
        units = response.json()
        assert isinstance(units, list)

    def test_get_unit_details(self, client: Client, auth_headers: dict):
        """Test getting detailed unit information."""
        response = client.get("/api/v1/curriculum/units/1", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            unit = response.json()
            assert "id" in unit
            assert "name" in unit
            assert "subject_id" in unit

    def test_list_unit_topics(self, client: Client, auth_headers: dict):
        """Test getting topics within a unit."""
        response = client.get("/api/v1/curriculum/units/1/topics", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            topics = response.json()
            assert isinstance(topics, list)


class TestTopics:
    """Test topic endpoints."""

    def test_list_all_topics(self, client: Client, auth_headers: dict):
        """Test getting list of all topics."""
        response = client.get("/api/v1/curriculum/topics", headers=auth_headers)
        assert response.status_code == 200
        topics = response.json()
        assert isinstance(topics, list)

    def test_get_topic_details(self, client: Client, auth_headers: dict):
        """Test getting detailed topic information."""
        response = client.get("/api/v1/curriculum/topics/1", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            topic = response.json()
            assert "id" in topic
            assert "name" in topic
            assert "unit_id" in topic

    def test_list_topic_learning_outcomes(self, client: Client, auth_headers: dict):
        """Test getting learning outcomes for a topic."""
        response = client.get("/api/v1/curriculum/topics/1/outcomes", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            outcomes = response.json()
            assert isinstance(outcomes, list)


class TestLearningOutcomes:
    """Test learning outcome endpoints."""

    def test_list_all_outcomes(self, client: Client, auth_headers: dict):
        """Test getting list of all learning outcomes."""
        response = client.get("/api/v1/curriculum/outcomes", headers=auth_headers)
        assert response.status_code == 200
        outcomes = response.json()
        assert isinstance(outcomes, list)

    def test_get_outcome_details(self, client: Client, auth_headers: dict):
        """Test getting detailed learning outcome information."""
        response = client.get("/api/v1/curriculum/outcomes/1", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            outcome = response.json()
            assert "id" in outcome
            assert "description" in outcome
            assert "topic_id" in outcome


class TestCurriculumHierarchy:
    """Test full curriculum hierarchy traversal."""

    def test_full_curriculum_tree(self, client: Client, auth_headers: dict):
        """Test retrieving full curriculum hierarchy."""
        response = client.get("/api/v1/curriculum", headers=auth_headers)
        assert response.status_code == 200
        curriculum = response.json()
        # Should contain all subjects with nested structure
        assert isinstance(curriculum, (dict, list))
