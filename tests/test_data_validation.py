import pytest
from src.app import activities


class TestDataValidation:
    """Test data validation and structure."""

    def test_activities_data_structure(self):
        """Test that all activities have the required data structure."""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            # Check that all required fields are present
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
            
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check constraints
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
            
            # Check that all participants are valid email-like strings
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert "." in participant

    def test_activity_names_are_unique(self):
        """Test that all activity names are unique (case-insensitive)."""
        activity_names_lower = [name.lower() for name in activities.keys()]
        assert len(activity_names_lower) == len(set(activity_names_lower))

    def test_participant_emails_are_unique_per_activity(self):
        """Test that participant emails are unique within each activity."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert len(participants) == len(set(participants)), \
                f"Activity '{activity_name}' has duplicate participants"

    def test_activities_have_reasonable_data(self):
        """Test that activities have reasonable data values."""
        for activity_name, activity_data in activities.items():
            # Description should not be empty
            assert len(activity_data["description"].strip()) > 0
            
            # Schedule should not be empty
            assert len(activity_data["schedule"].strip()) > 0
            
            # Max participants should be reasonable (between 1 and 100)
            assert 1 <= activity_data["max_participants"] <= 100
            
            # Activity name should not be empty
            assert len(activity_name.strip()) > 0

    def test_sample_activities_exist(self):
        """Test that expected sample activities exist."""
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in expected_activities:
            assert activity in activities, f"Expected activity '{activity}' not found"

    def test_email_format_validation(self):
        """Test that existing participant emails follow basic format rules."""
        for activity_name, activity_data in activities.items():
            for email in activity_data["participants"]:
                # Basic email validation
                assert "@" in email
                assert email.count("@") == 1
                
                local, domain = email.split("@")
                assert len(local) > 0
                assert len(domain) > 0
                assert "." in domain
                
                # Check for common invalid characters
                invalid_chars = [" ", "\t", "\n", "\r"]
                for char in invalid_chars:
                    assert char not in email