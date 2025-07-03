"""
Base prompts for the Hotel Booking AI Agent.
"""
from typing import Dict, Any
from pydantic import BaseModel

class BasePrompt(BaseModel):
    """Base class for prompts."""
    template: str
    
    def format(self, **kwargs) -> str:
        """Format the prompt template with the given variables."""
        return self.template.format(**kwargs)

class SystemPrompts:
    """System prompts for different functionalities."""
    
    BOOKING_AGENT = BasePrompt(
        template="""You are an AI hotel booking assistant for {hotel_name}. 
Your role is to help guests with bookings, answer questions about the hotel, and manage reservations.

Hotel Information:
- Name: {hotel_name}
- Address: {hotel_address}
- Check-in time: {check_in_time}
- Check-out time: {check_out_time}

Available room types:
{room_types}

Hotel policies:
{policies}

Please maintain a professional and helpful tone. Always verify all booking details before confirmation."""
    )
    
    INTENT_CLASSIFIER = BasePrompt(
        template="""Analyze the user's message and determine their primary intent.
Possible intents:
- booking: User wants to make a new booking
- rescheduling: User wants to modify an existing booking
- cancellation: User wants to cancel a booking
- inquiry: User has questions about the hotel
- confirmation: User wants to confirm booking details

User message: {message}

Respond with the intent and confidence level in JSON format."""
    )

class BookingPrompts:
    """Prompts for booking-related interactions."""
    
    COLLECT_DATES = BasePrompt(
        template="""I need to collect check-in and check-out dates for your stay at {hotel_name}.
Please provide:
1. Your preferred check-in date
2. Your preferred check-out date

Current dates (if any):
Check-in: {check_in_date}
Check-out: {check_out_date}"""
    )
    
    COLLECT_ROOM_TYPE = BasePrompt(
        template="""Please select your preferred room type from the following options:

{room_types}

Each room type includes:
- Free Wi-Fi
- Daily housekeeping
- Room service
- Complimentary breakfast

Current selection (if any): {current_room_type}"""
    )
    
    COLLECT_GUESTS = BasePrompt(
        template="""How many guests will be staying?
Please specify:
1. Number of adults (18+ years)
2. Number of children (0-17 years)

Current numbers (if any):
Adults: {num_adults}
Children: {num_children}"""
    )

class ConfirmationPrompts:
    """Prompts for confirmation-related interactions."""
    
    BOOKING_SUMMARY = BasePrompt(
        template="""Please review your booking details:

Booking ID: {booking_id}
Guest: {guest_name}
Check-in: {check_in_date}
Check-out: {check_out_date}
Room Type: {room_type}
Guests: {num_adults} adults, {num_children} children

Total nights: {total_nights}
Room rate: ${room_rate} per night
Total amount: ${total_amount}

Is this information correct? Please confirm to proceed with the booking."""
    )
    
    MODIFICATION_SUMMARY = BasePrompt(
        template="""Please review the changes to your booking:

Booking ID: {booking_id}

Original details:
{original_details}

New details:
{new_details}

Please confirm these changes."""
    ) 