"""
LangGraph implementation for hotel booking conversation flow.
"""
from typing import Dict, Any, List, Tuple, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field

from ..services.booking import BookingService
from ..llm.base import BaseLLMClient
from ..prompts.base import SystemPrompts
from ..config import HOTEL_CONFIG
from ..utils.date_parser import DateParser

class ConversationState(BaseModel):
    """State model for the conversation graph."""
    messages: List[HumanMessage | AIMessage | SystemMessage] = Field(default_factory=list)
    current_intent: str | None = None
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    booking_id: str | None = None
    error: str | None = None

def create_conversation_graph(
    llm_client: BaseLLMClient,
    booking_service: BookingService
) -> StateGraph:
    """Create the conversation graph for hotel booking flow."""
    
    # Define the workflow
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    
    # 1. Intent Detection Node
    async def detect_intent(state: ConversationState) -> ConversationState:
        """Detect user intent from the last message."""
        if not state.messages:
            return state
            
        last_message = state.messages[-1].content
        prompt = SystemPrompts.INTENT_CLASSIFIER.format(message=last_message)
        
        response = await llm_client.generate_structured_response(
            messages=[SystemMessage(content=prompt)],
            response_model=BaseModel
        )
        
        state.current_intent = response.dict()["intent"]
        return state
    
    workflow.add_node("detect_intent", detect_intent)
    
    # 2. Booking Flow Node
    async def handle_booking(state: ConversationState) -> ConversationState:
        """Handle the booking conversation flow."""
        if not state.collected_data:
            # Start collecting booking information
            response = "When would you like to check in and check out?"
            state.messages.append(AIMessage(content=response))
            return state
            
        if "dates" not in state.collected_data:
            # Extract dates from last message
            last_message = state.messages[-1].content
            dates = DateParser.extract_dates(last_message)
            
            if dates:
                # Validate date range
                is_valid, error_msg = DateParser.is_valid_date_range(
                    dates["check_in"],
                    dates["check_out"]
                )
                
                if is_valid:
                    state.collected_data["dates"] = dates
                    # Ask for room type
                    room_types = "\n".join(f"- {name}" for name in HOTEL_CONFIG["room_types"].values())
                    response = f"What type of room would you prefer? Available options:\n{room_types}"
                else:
                    response = f"I couldn't use those dates: {error_msg}. Please provide different dates."
            else:
                response = "I couldn't understand the dates. Please provide check-in and check-out dates in a format like 'DD/MM/YYYY' or 'Month DD, YYYY'."
            
            state.messages.append(AIMessage(content=response))
            return state
            
        if "room_type" not in state.collected_data:
            # Extract room type from last message
            last_message = state.messages[-1].content.lower()
            room_type = None
            
            for key, name in HOTEL_CONFIG["room_types"].items():
                if key in last_message or name.lower() in last_message:
                    room_type = key
                    break
            
            if room_type:
                state.collected_data["room_type"] = room_type
                response = "Please provide your name and email for the booking."
            else:
                room_types = "\n".join(f"- {name}" for name in HOTEL_CONFIG["room_types"].values())
                response = f"I didn't catch that. Please choose from these room types:\n{room_types}"
            
            state.messages.append(AIMessage(content=response))
            return state
            
        if "guest" not in state.collected_data:
            # Extract guest information from last message
            last_message = state.messages[-1].content
            
            # TODO: Implement better guest info extraction
            # For now, just store the message as guest info
            state.collected_data["guest"] = {"info": last_message}
            
            try:
                # Create booking
                booking = await booking_service.create(state.collected_data)
                state.booking_id = str(booking.id)
                confirmation = await booking_service.generate_confirmation_message(booking)
                state.messages.append(AIMessage(content=confirmation))
            except ValueError as e:
                state.error = str(e)
                state.messages.append(AIMessage(content=f"Error creating booking: {str(e)}"))
            
            return state
            
        return state
        
    workflow.add_node("booking_flow", handle_booking)
    
    # 3. Rescheduling Flow Node
    async def handle_rescheduling(state: ConversationState) -> ConversationState:
        """Handle the rescheduling conversation flow."""
        if not state.booking_id:
            response = "Please provide your booking ID to reschedule."
            state.messages.append(AIMessage(content=response))
            return state
            
        booking = await booking_service.get(state.booking_id)
        if not booking:
            response = f"Booking {state.booking_id} not found."
            state.messages.append(AIMessage(content=response))
            state.error = "Booking not found"
            return state
            
        if "new_dates" not in state.collected_data:
            # Try to extract dates from last message
            last_message = state.messages[-1].content
            dates = DateParser.extract_dates(last_message)
            
            if dates:
                # Validate date range
                is_valid, error_msg = DateParser.is_valid_date_range(
                    dates["check_in"],
                    dates["check_out"]
                )
                
                if is_valid:
                    state.collected_data["new_dates"] = dates
                    try:
                        updated_booking = await booking_service.update(
                            state.booking_id,
                            {
                                "check_in_date": dates["check_in"],
                                "check_out_date": dates["check_out"]
                            }
                        )
                        confirmation = await booking_service.generate_confirmation_message(updated_booking)
                        state.messages.append(AIMessage(content=confirmation))
                    except ValueError as e:
                        state.error = str(e)
                        state.messages.append(AIMessage(content=f"Error rescheduling booking: {str(e)}"))
                else:
                    response = f"I couldn't use those dates: {error_msg}. Please provide different dates."
                    state.messages.append(AIMessage(content=response))
            else:
                response = "What dates would you like to reschedule to? Please provide dates in a format like 'DD/MM/YYYY' or 'Month DD, YYYY'."
                state.messages.append(AIMessage(content=response))
            
            return state
            
        return state
        
    workflow.add_node("rescheduling_flow", handle_rescheduling)
    
    # 4. Inquiry Flow Node
    async def handle_inquiry(state: ConversationState) -> ConversationState:
        """Handle general inquiries about the hotel."""
        last_message = state.messages[-1].content
        prompt = f"""Based on the following hotel information, please answer the user's question:

Hotel Information:
{HOTEL_CONFIG}

User's question: {last_message}"""
        
        response = await llm_client.generate_response(
            messages=[SystemMessage(content=prompt)]
        )
        state.messages.append(AIMessage(content=response.content))
        return state
        
    workflow.add_node("inquiry_flow", handle_inquiry)
    
    # Add edges
    
    # From intent detection to specific flows
    workflow.add_edge("detect_intent", lambda x: {
        "booking_flow": x.current_intent == "booking",
        "rescheduling_flow": x.current_intent == "rescheduling",
        "inquiry_flow": x.current_intent == "inquiry",
        END: x.error is not None
    })
    
    # From flows back to intent detection for next message
    workflow.add_edge("booking_flow", lambda x: "detect_intent" if not x.error else END)
    workflow.add_edge("rescheduling_flow", lambda x: "detect_intent" if not x.error else END)
    workflow.add_edge("inquiry_flow", lambda x: "detect_intent" if not x.error else END)
    
    # Set entry point
    workflow.set_entry_point("detect_intent")
    
    return workflow

class LangGraphManager:
    """Manager class for LangGraph conversation flow."""
    
    def __init__(
        self,
        llm_client: BaseLLMClient,
        booking_service: BookingService
    ):
        """Initialize LangGraph manager."""
        self.graph = create_conversation_graph(llm_client, booking_service)
        self.states: Dict[str, ConversationState] = {}
    
    def get_state(self, user_id: str) -> ConversationState:
        """Get or create conversation state for a user."""
        if user_id not in self.states:
            self.states[user_id] = ConversationState()
        return self.states[user_id]
    
    async def handle_message(self, user_id: str, message: str) -> str:
        """Handle incoming user message using LangGraph flow."""
        state = self.get_state(user_id)
        state.messages.append(HumanMessage(content=message))
        
        # Run the graph
        final_state = await self.graph.arun(state)
        
        # Get the last AI message as response
        if final_state.messages and isinstance(final_state.messages[-1], AIMessage):
            return final_state.messages[-1].content
        return "I apologize, but I couldn't process your request. Please try again." 