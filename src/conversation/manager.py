"""
Conversation manager implementation.
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel

from ..llm.base import BaseLLMClient, Message
from ..services.booking import BookingService
from ..prompts.base import SystemPrompts
from ..config import HOTEL_CONFIG

class ConversationState(BaseModel):
    """Conversation state model."""
    user_id: str
    current_intent: Optional[str] = None
    current_booking_id: Optional[UUID] = None
    collected_data: Dict[str, Any] = {}
    last_message: Optional[str] = None
    context: Dict[str, Any] = {}

class ConversationManager:
    """Manages conversation flow and state."""
    
    def __init__(
        self,
        llm_client: BaseLLMClient,
        booking_service: BookingService
    ):
        """Initialize conversation manager."""
        self.llm_client = llm_client
        self.booking_service = booking_service
        self.system_prompts = SystemPrompts()
        self.states: Dict[str, ConversationState] = {}
    
    def get_state(self, user_id: str) -> ConversationState:
        """Get or create conversation state for a user."""
        if user_id not in self.states:
            self.states[user_id] = ConversationState(user_id=user_id)
        return self.states[user_id]
    
    async def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent from message."""
        prompt = self.system_prompts.INTENT_CLASSIFIER.format(message=message)
        response = await self.llm_client.generate_structured_response(
            messages=[Message(role="user", content=prompt)],
            response_model=BaseModel
        )
        return response.dict()
    
    async def handle_message(self, user_id: str, message: str) -> str:
        """Handle incoming user message."""
        # Get conversation state
        state = self.get_state(user_id)
        state.last_message = message
        
        # If no current intent, detect it
        if not state.current_intent:
            intent_data = await self.detect_intent(message)
            state.current_intent = intent_data["intent"]
            
            # Initialize context based on intent
            if state.current_intent == "booking":
                state.collected_data = {}
            elif state.current_intent == "rescheduling":
                if not state.current_booking_id:
                    return "Please provide your booking ID to reschedule."
        
        # Handle intent
        if state.current_intent == "booking":
            return await self._handle_booking(state, message)
        elif state.current_intent == "rescheduling":
            return await self._handle_rescheduling(state, message)
        elif state.current_intent == "cancellation":
            return await self._handle_cancellation(state, message)
        elif state.current_intent == "inquiry":
            return await self._handle_inquiry(state, message)
        else:
            return "I'm not sure how to help with that. Could you please rephrase?"
    
    async def _handle_booking(self, state: ConversationState, message: str) -> str:
        """Handle booking conversation flow."""
        # If no data collected yet, start with dates
        if not state.collected_data:
            return "When would you like to check in and check out?"
        
        # If dates missing, try to extract from message
        if "dates" not in state.collected_data:
            # TODO: Extract dates from message
            pass
        
        # If room type missing, ask for it
        if "room_type" not in state.collected_data:
            return f"What type of room would you prefer? Available options:\n" + \
                "\n".join(f"- {name}" for name in HOTEL_CONFIG["room_types"].values())
        
        # If guest info missing, ask for it
        if "guest" not in state.collected_data:
            return "Please provide your name and email for the booking."
        
        # Create booking
        try:
            booking = await self.booking_service.create(state.collected_data)
            state.current_booking_id = booking.id
            return await self.booking_service.generate_confirmation_message(booking)
        except ValueError as e:
            return f"Error creating booking: {str(e)}"
    
    async def _handle_rescheduling(self, state: ConversationState, message: str) -> str:
        """Handle rescheduling conversation flow."""
        if not state.current_booking_id:
            # Try to extract booking ID from message
            # TODO: Extract booking ID
            return "Please provide your booking ID to reschedule."
        
        # Get existing booking
        booking = await self.booking_service.get(state.current_booking_id)
        if not booking:
            return f"Booking {state.current_booking_id} not found."
        
        # If no new dates collected, ask for them
        if "new_dates" not in state.collected_data:
            return "What dates would you like to reschedule to?"
        
        # Update booking
        try:
            updated_booking = await self.booking_service.update(
                state.current_booking_id,
                {"check_in_date": state.collected_data["new_dates"]["check_in"],
                 "check_out_date": state.collected_data["new_dates"]["check_out"]}
            )
            return await self.booking_service.generate_confirmation_message(updated_booking)
        except ValueError as e:
            return f"Error rescheduling booking: {str(e)}"
    
    async def _handle_cancellation(self, state: ConversationState, message: str) -> str:
        """Handle cancellation conversation flow."""
        if not state.current_booking_id:
            # Try to extract booking ID from message
            # TODO: Extract booking ID
            return "Please provide your booking ID to cancel."
        
        # Get existing booking
        booking = await self.booking_service.get(state.current_booking_id)
        if not booking:
            return f"Booking {state.current_booking_id} not found."
        
        # Cancel booking
        if await self.booking_service.delete(state.current_booking_id):
            return "Your booking has been cancelled successfully."
        else:
            return "Error cancelling your booking. Please try again."
    
    async def _handle_inquiry(self, state: ConversationState, message: str) -> str:
        """Handle general inquiries about the hotel."""
        # Use LLM to generate response based on hotel config
        prompt = f"""Based on the following hotel information, please answer the user's question:

Hotel Information:
{HOTEL_CONFIG}

User's question: {message}"""
        
        response = await self.llm_client.generate_response(
            messages=[Message(role="user", content=prompt)]
        )
        return response.content 