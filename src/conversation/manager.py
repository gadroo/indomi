"""
Conversation manager implementation.
"""
from typing import Dict, Any, Optional
from uuid import UUID

from ..llm.base import BaseLLMClient
from ..services.booking import BookingService
from .langgraph_flow import LangGraphManager

class ConversationManager:
    """Manages conversation flow and state using LangGraph."""
    
    def __init__(
        self,
        llm_client: BaseLLMClient,
        booking_service: BookingService
    ):
        """Initialize conversation manager."""
        self.langgraph_manager = LangGraphManager(llm_client, booking_service)
    
    async def handle_message(self, user_id: str, message: str) -> str:
        """Handle incoming user message."""
        return await self.langgraph_manager.handle_message(user_id, message) 