"""
Tests for the main application module.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.app import app
from src.config import HOTEL_CONFIG

client = TestClient(app)

@pytest.fixture
def sample_booking():
    """Create a sample booking for testing."""
    now = datetime.now()
    return {
        "check_in_date": (now + timedelta(days=1)).isoformat(),
        "check_out_date": (now + timedelta(days=3)).isoformat(),
        "room_type": "standard",
        "num_adults": 2,
        "num_children": 1,
        "guest_name": "John Doe",
        "guest_email": "john@example.com",
        "guest_phone": "+1234567890"
    }

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hotel Booking AI Agent is running"}

def test_get_hotel_info():
    """Test getting hotel information."""
    response = client.get("/hotel/info")
    assert response.status_code == 200
    assert response.json() == HOTEL_CONFIG

def test_webhook_verification():
    """Test webhook verification endpoint."""
    params = {
        "mode": "subscribe",
        "token": "test_token",  # This should match the app secret in the test environment
        "challenge": "1234567890"
    }
    response = client.get("/webhook", params=params)
    assert response.status_code in [200, 403]  # Depends on token validation

def test_webhook_processing():
    """Test webhook processing endpoint."""
    webhook_data = {
        "entry": [{
            "messaging": [{
                "sender": {"id": "user123"},
                "message": {"text": "Hello"}
            }]
        }]
    }
    response = client.post("/webhook", json=webhook_data)
    assert response.status_code == 200

def test_create_reservation(sample_booking):
    """Test creating a reservation."""
    response = client.post("/reservations", json=sample_booking)
    assert response.status_code == 200
    assert "booking_id" in response.json()
    assert response.json()["status"] == "confirmed"

def test_get_reservation(sample_booking):
    """Test getting a reservation."""
    # First create a reservation
    create_response = client.post("/reservations", json=sample_booking)
    booking_id = create_response.json()["booking_id"]

    # Then get it
    response = client.get(f"/reservations/{booking_id}")
    assert response.status_code == 200
    assert response.json()["room_type"] == sample_booking["room_type"]
    assert response.json()["guest_name"] == sample_booking["guest_name"]

def test_get_nonexistent_reservation():
    """Test getting a non-existent reservation."""
    response = client.get("/reservations/nonexistent-id")
    assert response.status_code == 404

def test_update_reservation(sample_booking):
    """Test updating a reservation."""
    # First create a reservation
    create_response = client.post("/reservations", json=sample_booking)
    booking_id = create_response.json()["booking_id"]

    # Then update it
    updates = {
        "num_adults": 3,
        "num_children": 2
    }
    response = client.put(f"/reservations/{booking_id}", json=updates)
    assert response.status_code == 200
    assert response.json()["status"] == "updated"

    # Verify the update
    get_response = client.get(f"/reservations/{booking_id}")
    assert get_response.json()["num_adults"] == 3
    assert get_response.json()["num_children"] == 2

def test_delete_reservation(sample_booking):
    """Test deleting a reservation."""
    # First create a reservation
    create_response = client.post("/reservations", json=sample_booking)
    booking_id = create_response.json()["booking_id"]

    # Then delete it
    response = client.delete(f"/reservations/{booking_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # Verify deletion
    get_response = client.get(f"/reservations/{booking_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_webhook_with_conversation():
    """Test webhook with conversation flow."""
    with patch('src.instagram_client.InstagramClient.send_message') as mock_send:
        mock_send.return_value = True
        
        # Simulate booking request
        webhook_data = {
            "entry": [{
                "messaging": [{
                    "sender": {"id": "user123"},
                    "message": {"text": "I want to book a room"}
                }]
            }]
        }
        response = client.post("/webhook", json=webhook_data)
        assert response.status_code == 200
        
        # Verify bot responded
        mock_send.assert_called() 