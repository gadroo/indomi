"""
State management module for the Hotel Booking AI Agent using LangGraph.
"""
from typing import Dict, List, Optional, Tuple, TypedDict, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from langgraph.graph import Graph, StateGraph
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from loguru import logger
from config import GROQ_API_KEY, logger

# State Definitions
class UserInfo(BaseModel):
    """User information for booking."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class BookingDetails(BaseModel):
    """Details for a hotel booking."""
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    room_type: Optional[str] = None
    num_adults: Optional[int] = None
    num_children: Optional[int] = None
    booking_id: Optional[str] = None
    status: str = "pending"

class ConversationState(BaseModel):
    """Complete state of the conversation."""
    current_state: str = "initial"
    user_info: UserInfo = Field(default_factory=UserInfo)
    booking_details: BookingDetails = Field(default_factory=BookingDetails)
    last_user_message: Optional[str] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    intent: Optional[str] = None
    error_context: Optional[str] = None

# State Graph Configuration
def create_state_graph() -> StateGraph:
    """Create the state management graph using LangGraph."""
    
    # Initialize LLM
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=1000
    )

    # Define state transitions
    workflow = StateGraph(nodes=["initial", "identify_intent", "collect_info", "confirm_booking", "handle_error"])

    # Add nodes with their respective handlers
    workflow.add_node("initial", initial_handler)
    workflow.add_node("identify_intent", identify_intent_handler)
    workflow.add_node("collect_info", collect_info_handler)
    workflow.add_node("confirm_booking", confirm_booking_handler)
    workflow.add_node("handle_error", handle_error_handler)

    # Define edges
    workflow.add_edge("initial", "identify_intent")
    workflow.add_edge("identify_intent", "collect_info")
    workflow.add_edge("collect_info", "confirm_booking")
    workflow.add_edge("confirm_booking", "collect_info")  # For modifications
    workflow.add_edge("*", "handle_error")  # Error handling from any state
    
    # Conditional edges
    workflow.add_conditional_edges(
        "identify_intent",
        lambda x: "collect_info" if x.get("intent") in ["booking", "rescheduling"] else "handle_questions"
    )

    return workflow

# State Handlers
async def initial_handler(state: ConversationState) -> ConversationState:
    """Handle initial state and setup."""
    logger.info(f"Entering initial state handler")
    state.current_state = "initial"
    return state

async def identify_intent_handler(state: ConversationState) -> ConversationState:
    """Identify user intent from message."""
    logger.info(f"Identifying intent from message: {state.last_user_message}")
    # Intent classification logic here
    return state

async def collect_info_handler(state: ConversationState) -> ConversationState:
    """Collect necessary information based on intent."""
    logger.info(f"Collecting information for intent: {state.intent}")
    # Information collection logic here
    return state

async def confirm_booking_handler(state: ConversationState) -> ConversationState:
    """Confirm booking details and finalize."""
    logger.info(f"Confirming booking: {state.booking_details}")
    # Booking confirmation logic here
    return state

async def handle_error_handler(state: ConversationState) -> ConversationState:
    """Handle errors and exceptions."""
    logger.error(f"Error in state {state.current_state}: {state.error_context}")
    # Error handling logic here
    return state

# Helper functions for state transitions
def validate_dates(check_in: datetime, check_out: datetime) -> Tuple[bool, str]:
    """Validate booking dates."""
    if check_in >= check_out:
        return False, "Check-out date must be after check-in date"
    if check_in < datetime.now():
        return False, "Check-in date cannot be in the past"
    return True, ""

def validate_booking_details(booking: BookingDetails) -> Tuple[bool, str]:
    """Validate complete booking details."""
    if not all([booking.check_in_date, booking.check_out_date, booking.room_type,
                booking.num_adults]):
        return False, "Missing required booking information"
    return validate_dates(booking.check_in_date, booking.check_out_date) 