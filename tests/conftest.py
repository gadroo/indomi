"""
Shared test fixtures for the Hotel Booking AI Agent.
"""
import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict('os.environ', {
        'GROQ_API_KEY': 'test_groq_key',
        'INSTAGRAM_ACCESS_TOKEN': 'test_instagram_token',
        'INSTAGRAM_APP_ID': 'test_app_id',
        'INSTAGRAM_APP_SECRET': 'test_app_secret',
        'DEBUG': 'True',
        'LOG_LEVEL': 'INFO'
    }):
        yield

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def test_log_dir(tmp_path):
    """Create a temporary log directory for testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def sample_user_info():
    """Create sample user information for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    }

@pytest.fixture
def sample_booking_details():
    """Create sample booking details for testing."""
    now = datetime.now()
    return {
        "check_in_date": now + timedelta(days=1),
        "check_out_date": now + timedelta(days=3),
        "room_type": "standard",
        "num_adults": 2,
        "num_children": 1
    }

@pytest.fixture
def sample_conversation_history():
    """Create sample conversation history for testing."""
    return [
        {"role": "user", "content": "I want to book a room"},
        {"role": "assistant", "content": "I'll help you book a room. When would you like to check in?"},
        {"role": "user", "content": "Tomorrow for 2 nights"},
    ]

@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response for testing."""
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "I understand you want to book a room. Let me help you with that."
            }
        }]
    }

@pytest.fixture
def mock_instagram_response():
    """Create a mock Instagram API response for testing."""
    return {
        "data": [{
            "id": "msg_123",
            "text": "Hello",
            "timestamp": "1234567890"
        }]
    }

@pytest.fixture
def mock_storage_data():
    """Create mock storage data for testing."""
    now = datetime.now()
    return {
        "reservations": [
            {
                "booking_id": "test-booking-1",
                "check_in_date": (now + timedelta(days=1)).isoformat(),
                "check_out_date": (now + timedelta(days=3)).isoformat(),
                "room_type": "standard",
                "num_adults": 2,
                "num_children": 1,
                "guest_name": "John Doe",
                "guest_email": "john@example.com",
                "guest_phone": "+1234567890",
                "status": "confirmed",
                "created_at": now.isoformat()
            }
        ],
        "last_updated": now.isoformat()
    } 