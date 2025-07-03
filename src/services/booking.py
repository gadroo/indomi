"""
Booking service implementation.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from .base import BaseService
from ..models.booking import Booking, Guest, RoomDetails, BookingStatus
from ..storage.base import BaseStorage
from ..llm.base import BaseLLMClient, Message
from ..prompts.base import BookingPrompts, ConfirmationPrompts

class BookingService(BaseService[Booking]):
    """Booking service implementation."""
    
    def __init__(self, storage: BaseStorage[Booking], llm_client: BaseLLMClient):
        """Initialize booking service."""
        super().__init__(storage, llm_client)
        self.booking_prompts = BookingPrompts()
        self.confirmation_prompts = ConfirmationPrompts()
    
    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate booking data."""
        # Validate dates
        check_in = datetime.fromisoformat(data["check_in_date"])
        check_out = datetime.fromisoformat(data["check_out_date"])
        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date")
        
        # Validate guest information
        if not data.get("guest", {}).get("email"):
            raise ValueError("Guest email is required")
        
        # Validate room details
        if data.get("room", {}).get("num_adults", 0) < 1:
            raise ValueError("At least one adult guest is required")
        
        return data
    
    async def create(self, data: Dict[str, Any]) -> Booking:
        """Create a new booking."""
        # Validate data
        validated_data = await self.validate(data)
        
        # Create models
        guest = Guest(**validated_data["guest"])
        room = RoomDetails(**validated_data["room"])
        
        # Create booking
        booking = Booking(
            guest=guest,
            room=room,
            check_in_date=datetime.fromisoformat(validated_data["check_in_date"]),
            check_out_date=datetime.fromisoformat(validated_data["check_out_date"]),
            total_amount=room.rate * (
                datetime.fromisoformat(validated_data["check_out_date"]) -
                datetime.fromisoformat(validated_data["check_in_date"])
            ).days
        )
        
        # Store booking
        return await self.storage.create(booking)
    
    async def get(self, id: UUID) -> Optional[Booking]:
        """Get a booking by ID."""
        return await self.storage.get(id)
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Booking:
        """Update an existing booking."""
        # Get existing booking
        booking = await self.get(id)
        if not booking:
            raise ValueError(f"Booking {id} not found")
        
        # Validate data
        validated_data = await self.validate({**booking.dict(), **data})
        
        # Update booking
        updated_booking = Booking(
            id=booking.id,
            guest=Guest(**validated_data["guest"]),
            room=RoomDetails(**validated_data["room"]),
            check_in_date=datetime.fromisoformat(validated_data["check_in_date"]),
            check_out_date=datetime.fromisoformat(validated_data["check_out_date"]),
            status=booking.status,
            total_amount=RoomDetails(**validated_data["room"]).rate * (
                datetime.fromisoformat(validated_data["check_out_date"]) -
                datetime.fromisoformat(validated_data["check_in_date"])
            ).days,
            created_at=booking.created_at
        )
        
        # Store updated booking
        return await self.storage.update(id, updated_booking)
    
    async def delete(self, id: UUID) -> bool:
        """Delete a booking."""
        return await self.storage.delete(id)
    
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Booking]:
        """List all bookings, optionally filtered."""
        return await self.storage.list(filters)
    
    async def confirm_booking(self, id: UUID) -> Booking:
        """Confirm a booking."""
        booking = await self.get(id)
        if not booking:
            raise ValueError(f"Booking {id} not found")
        
        booking.status.is_confirmed = True
        booking.status.last_updated = datetime.now()
        booking.updated_at = datetime.now()
        
        return await self.storage.update(id, booking)
    
    async def generate_confirmation_message(self, booking: Booking) -> str:
        """Generate a confirmation message for a booking."""
        prompt = self.confirmation_prompts.BOOKING_SUMMARY.format(
            booking_id=booking.id,
            guest_name=booking.guest.name,
            check_in_date=booking.check_in_date.date(),
            check_out_date=booking.check_out_date.date(),
            room_type=booking.room.room_type,
            num_adults=booking.room.num_adults,
            num_children=booking.room.num_children,
            total_nights=booking.calculate_nights(),
            room_rate=booking.room.rate,
            total_amount=booking.total_amount
        )
        
        response = await self.llm_client.generate_response(
            messages=[Message(role="user", content=prompt)]
        )
        
        return response.content 