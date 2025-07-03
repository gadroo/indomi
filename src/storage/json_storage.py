"""
JSON file storage implementation.
"""
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
from uuid import UUID
from pydantic import BaseModel

from .base import BaseStorage, T

class JSONStorage(BaseStorage[T]):
    """JSON file storage implementation."""
    
    def __init__(self, file_path: Path, model_class: Type[T]):
        """Initialize JSON storage."""
        self.file_path = file_path
        self.model_class = model_class
        self.lock = asyncio.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text("[]")
    
    async def _read_data(self) -> List[Dict[str, Any]]:
        """Read data from JSON file."""
        async with self.lock:
            return json.loads(self.file_path.read_text())
    
    async def _write_data(self, data: List[Dict[str, Any]]):
        """Write data to JSON file."""
        async with self.lock:
            self.file_path.write_text(json.dumps(data, indent=2))
    
    async def create(self, item: T) -> T:
        """Create a new item."""
        data = await self._read_data()
        item_dict = item.dict()
        data.append(item_dict)
        await self._write_data(data)
        return item
    
    async def get(self, id: UUID) -> Optional[T]:
        """Get an item by ID."""
        data = await self._read_data()
        for item in data:
            if item["id"] == str(id):
                return self.model_class.parse_obj(item)
        return None
    
    async def update(self, id: UUID, item: T) -> T:
        """Update an existing item."""
        data = await self._read_data()
        for i, existing in enumerate(data):
            if existing["id"] == str(id):
                item_dict = item.dict()
                data[i] = item_dict
                await self._write_data(data)
                return item
        raise ValueError(f"Item with ID {id} not found")
    
    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID."""
        data = await self._read_data()
        original_length = len(data)
        data = [item for item in data if item["id"] != str(id)]
        if len(data) < original_length:
            await self._write_data(data)
            return True
        return False
    
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List all items, optionally filtered."""
        data = await self._read_data()
        if filters:
            filtered_data = []
            for item in data:
                match = True
                for key, value in filters.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            data = filtered_data
        return [self.model_class.parse_obj(item) for item in data]
    
    async def exists(self, id: UUID) -> bool:
        """Check if an item exists."""
        data = await self._read_data()
        return any(item["id"] == str(id) for item in data) 