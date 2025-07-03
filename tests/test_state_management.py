"""
Tests for the state management module.
"""
import pytest
from datetime import datetime, timedelta
from src.state_management import (
    UserInfo,
    BookingDetails,
    ConversationState,
    validate_dates,
    validate_booking_details
)

def test_user_info_creation():
    """Test UserInfo model creation."""
    user = UserInfo(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890"
    )
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.phone == "+1234567890"

def test_booking_details_creation():
    """Test BookingDetails model creation."""
    now = datetime.now()
    booking = BookingDetails(
        check_in_date=now + timedelta(days=1),
        check_out_date=now + timedelta(days=3),
        room_type="standard",
        num_adults=2,
        num_children=1
    )
    assert booking.room_type == "standard"
    assert booking.num_adults == 2
    assert booking.num_children == 1
    assert booking.status == "pending"

def test_conversation_state_creation():
    """Test ConversationState model creation."""
    state = ConversationState(
        current_state="initial",
        last_user_message="Hello"
    )
    assert state.current_state == "initial"
    assert state.last_user_message == "Hello"
    assert isinstance(state.user_info, UserInfo)
    assert isinstance(state.booking_details, BookingDetails)

def test_validate_dates():
    """Test date validation logic."""
    now = datetime.now()
    future1 = now + timedelta(days=1)
    future2 = now + timedelta(days=2)
    past = now - timedelta(days=1)

    # Valid dates
    is_valid, message = validate_dates(future1, future2)
    assert is_valid
    assert message == ""

    # Invalid: check-out before check-in
    is_valid, message = validate_dates(future2, future1)
    assert not is_valid
    assert "Check-out date must be after check-in date" in message

    # Invalid: check-in in past
    is_valid, message = validate_dates(past, future1)
    assert not is_valid
    assert "Check-in date cannot be in the past" in message

def test_validate_booking_details():
    """Test booking details validation."""
    now = datetime.now()
    valid_booking = BookingDetails(
        check_in_date=now + timedelta(days=1),
        check_out_date=now + timedelta(days=3),
        room_type="standard",
        num_adults=2
    )
    is_valid, message = validate_booking_details(valid_booking)
    assert is_valid
    assert message == ""

    # Test with missing required fields
    invalid_booking = BookingDetails()
    is_valid, message = validate_booking_details(invalid_booking)
    assert not is_valid
    assert "Missing required booking information" in message 