"""
Base storage implementation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from uuid import UUID
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseStorage(ABC, Generic[T]):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    async def create(self, item: T) -> T:
        """Create a new item."""
        pass
    
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """Get an item by ID."""
        pass
    
    @abstractmethod
    async def update(self, id: UUID, item: T) -> T:
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
    async def exists(self, id: UUID) -> bool:
        """Check if an item exists."""
        pass 