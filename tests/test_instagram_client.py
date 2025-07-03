"""
Tests for the Instagram client module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.instagram_client import InstagramClient

@pytest.fixture
def instagram_client():
    """Create an Instagram client instance for testing."""
    with patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'test_token',
        'INSTAGRAM_APP_ID': 'test_app_id',
        'INSTAGRAM_APP_SECRET': 'test_secret'
    }):
        return InstagramClient()

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.json.return_value = {"data": [{"id": "123", "text": "Hello"}]}
    mock.raise_for_status.return_value = None
    return mock

def test_client_initialization(instagram_client):
    """Test client initialization."""
    assert instagram_client.access_token == 'test_token'
    assert instagram_client.app_id == 'test_app_id'
    assert instagram_client.app_secret == 'test_secret'

@pytest.mark.asyncio
async def test_send_message(instagram_client, mock_response):
    """Test sending a message."""
    with patch('requests.post', return_value=mock_response):
        success = await instagram_client.send_message("user123", "Hello!")
        assert success

@pytest.mark.asyncio
async def test_get_messages(instagram_client, mock_response):
    """Test getting messages."""
    with patch('requests.get', return_value=mock_response):
        messages = await instagram_client.get_messages("user123")
        assert len(messages) == 1
        assert messages[0]["id"] == "123"

def test_verify_webhook(instagram_client):
    """Test webhook verification."""
    challenge = "1234567890"
    result = instagram_client.verify_webhook(
        mode="subscribe",
        token="test_secret",
        challenge=challenge
    )
    assert result == challenge

    # Test invalid verification
    result = instagram_client.verify_webhook(
        mode="invalid",
        token="wrong_token",
        challenge=challenge
    )
    assert result is None

def test_process_webhook(instagram_client):
    """Test webhook data processing."""
    # Valid webhook data
    webhook_data = {
        "entry": [{
            "messaging": [{
                "sender": {"id": "user123"},
                "message": {"text": "Hello"}
            }]
        }]
    }
    result = instagram_client.process_webhook(webhook_data)
    assert result is not None
    assert result["sender_id"] == "user123"
    assert result["message"] == "Hello"

    # Invalid webhook data
    invalid_data = {"entry": [{}]}
    result = instagram_client.process_webhook(invalid_data)
    assert result is None

@pytest.mark.asyncio
async def test_send_message_failure(instagram_client):
    """Test sending a message with API failure."""
    with patch('requests.post', side_effect=Exception("API Error")):
        success = await instagram_client.send_message("user123", "Hello!")
        assert not success

@pytest.mark.asyncio
async def test_get_messages_failure(instagram_client):
    """Test getting messages with API failure."""
    with patch('requests.get', side_effect=Exception("API Error")):
        messages = await instagram_client.get_messages("user123")
        assert len(messages) == 0 