"""
Base service implementation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from uuid import UUID
from pydantic import BaseModel

from ..storage.base import BaseStorage
from ..llm.base import BaseLLMClient

T = TypeVar("T", bound=BaseModel)

class BaseService(ABC, Generic[T]):
    """Abstract base class for services."""
    
    def __init__(self, storage: BaseStorage[T], llm_client: BaseLLMClient):
        """Initialize service."""
        self.storage = storage
        self.llm_client = llm_client
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new item."""
        pass
    
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """Get an item by ID."""
        pass
    
    @abstractmethod
    async def update(self, id: UUID, data: Dict[str, Any]) -> T:
        """Update an existing item."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID."""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List all items, optionally filtered."""
        pass
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data."""
        pass 