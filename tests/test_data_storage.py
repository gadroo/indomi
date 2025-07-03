"""
Tests for the data storage module.
"""
import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.data_storage import ReservationStorage

@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage file for testing."""
    storage_file = tmp_path / "test_reservations.json"
    return ReservationStorage(storage_file)

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

def test_storage_initialization(temp_storage):
    """Test storage initialization."""
    assert temp_storage.reservations_file.exists()
    data = json.loads(temp_storage.reservations_file.read_text())
    assert "reservations" in data
    assert isinstance(data["reservations"], list)
    assert "last_updated" in data

def test_create_reservation(temp_storage, sample_booking):
    """Test creating a new reservation."""
    booking_id = temp_storage.create_reservation(sample_booking)
    
    # Verify booking was created
    assert booking_id is not None
    reservation = temp_storage.get_reservation(booking_id)
    assert reservation is not None
    assert reservation["room_type"] == sample_booking["room_type"]
    assert reservation["guest_name"] == sample_booking["guest_name"]

def test_get_nonexistent_reservation(temp_storage):
    """Test getting a non-existent reservation."""
    reservation = temp_storage.get_reservation("nonexistent-id")
    assert reservation is None

def test_update_reservation(temp_storage, sample_booking):
    """Test updating an existing reservation."""
    # Create a reservation first
    booking_id = temp_storage.create_reservation(sample_booking)
    
    # Update the reservation
    updates = {
        "num_adults": 3,
        "num_children": 2
    }
    success = temp_storage.update_reservation(booking_id, updates)
    assert success
    
    # Verify updates
    updated = temp_storage.get_reservation(booking_id)
    assert updated["num_adults"] == 3
    assert updated["num_children"] == 2

def test_delete_reservation(temp_storage, sample_booking):
    """Test deleting a reservation."""
    # Create a reservation first
    booking_id = temp_storage.create_reservation(sample_booking)
    
    # Delete the reservation
    success = temp_storage.delete_reservation(booking_id)
    assert success
    
    # Verify deletion
    reservation = temp_storage.get_reservation(booking_id)
    assert reservation is None

def test_check_availability(temp_storage, sample_booking):
    """Test room availability checking."""
    now = datetime.now()
    
    # Initially should be available
    is_available = temp_storage.check_availability(
        now + timedelta(days=1),
        now + timedelta(days=3),
        "standard"
    )
    assert is_available
    
    # Create a booking
    temp_storage.create_reservation(sample_booking)
    
    # Should now be unavailable for same dates
    is_available = temp_storage.check_availability(
        datetime.fromisoformat(sample_booking["check_in_date"]),
        datetime.fromisoformat(sample_booking["check_out_date"]),
        "standard"
    )
    assert not is_available
    
    # Should be available for different dates
    is_available = temp_storage.check_availability(
        now + timedelta(days=10),
        now + timedelta(days=12),
        "standard"
    )
    assert is_available 