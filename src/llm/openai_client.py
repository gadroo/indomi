"""
OpenAI client implementation.
"""
from typing import List, Dict, Any, Optional
import json
from openai import AsyncOpenAI
from pydantic import BaseModel

from .base import BaseLLMClient, Message, LLMResponse
from ..config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS
)

class OpenAIClient(BaseLLMClient):
    """OpenAI client implementation."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.default_temperature = OPENAI_TEMPERATURE
        self.default_max_tokens = OPENAI_MAX_TOKENS

    async def generate_response(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[msg.dict() for msg in messages],
            temperature=temperature or self.default_temperature,
            max_tokens=max_tokens or self.default_max_tokens,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            raw_response=response
        )

    async def generate_structured_response(
        self,
        messages: List[Message],
        response_model: type[BaseModel],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseModel:
        """Generate a structured response from OpenAI."""
        # Add system message to enforce JSON output
        system_msg = Message(
            role="system",
            content="You must respond with valid JSON that matches the following Pydantic model structure: "
                   f"{response_model.schema_json()}"
        )
        messages = [system_msg] + messages
        
        response = await self.generate_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        # Parse the response into the model
        try:
            data = json.loads(response.content)
            return response_model.parse_obj(data)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response into {response_model.__name__}: {str(e)}") 