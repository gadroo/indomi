"""
Base LLM client implementation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Message(BaseModel):
    """Message model for LLM interactions."""
    role: str
    content: str

class LLMResponse(BaseModel):
    """Standard response model for LLM outputs."""
    content: str
    raw_response: Any = None

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def generate_structured_response(
        self,
        messages: List[Message],
        response_model: type[BaseModel],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseModel:
        """Generate a structured response from the LLM."""
        pass 