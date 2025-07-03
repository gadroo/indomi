"""
Booking-related data models.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class Guest(BaseModel):
    """Guest information model."""
    name: str
    email: str
    phone: Optional[str] = None
    preferences: Optional[dict] = Field(default_factory=dict)

class RoomDetails(BaseModel):
    """Room details model."""
    room_type: str
    rate: float
    num_adults: int = Field(ge=1)
    num_children: int = Field(ge=0)
    special_requests: Optional[str] = None

class BookingStatus(BaseModel):
    """Booking status model."""
    is_confirmed: bool = False
    is_paid: bool = False
    payment_status: str = "pending"
    check_in_status: str = "pending"
    last_updated: datetime = Field(default_factory=datetime.now)

class Booking(BaseModel):
    """Main booking model."""
    id: UUID = Field(default_factory=uuid4)
    guest: Guest
    room: RoomDetails
    check_in_date: datetime
    check_out_date: datetime
    status: BookingStatus = Field(default_factory=BookingStatus)
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator("check_out_date")
    def check_dates(cls, v, values):
        """Validate check-out date is after check-in date."""
        if "check_in_date" in values and v <= values["check_in_date"]:
            raise ValueError("Check-out date must be after check-in date")
        return v

    def calculate_nights(self) -> int:
        """Calculate the number of nights for the booking."""
        return (self.check_out_date - self.check_in_date).days

    def calculate_total_amount(self) -> float:
        """Calculate the total amount for the booking."""
        nights = self.calculate_nights()
        return self.room.rate * nights

    def update_status(self, **kwargs):
        """Update booking status."""
        for key, value in kwargs.items():
            if hasattr(self.status, key):
                setattr(self.status, key, value)
        self.status.last_updated = datetime.now()
        self.updated_at = datetime.now()

class BookingModification(BaseModel):
    """Booking modification model."""
    booking_id: UUID
    original_booking: Booking
    new_check_in_date: Optional[datetime] = None
    new_check_out_date: Optional[datetime] = None
    new_room_details: Optional[RoomDetails] = None
    modification_reason: str
    created_at: datetime = Field(default_factory=datetime.now)

class BookingCancellation(BaseModel):
    """Booking cancellation model."""
    booking_id: UUID
    cancellation_reason: str
    refund_amount: Optional[float] = None
    cancellation_fee: Optional[float] = None
    cancelled_at: datetime = Field(default_factory=datetime.now) 