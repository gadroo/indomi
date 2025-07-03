"""
Data storage module for managing hotel reservations.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from loguru import logger
from config import RESERVATIONS_FILE, MOCK_DATA_FILE

class ReservationStorage:
    """Handles storage and retrieval of hotel reservations."""
    
    def __init__(self):
        """Initialize the storage system."""
        self.reservations_file = RESERVATIONS_FILE
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure the storage file exists with proper structure."""
        if not self.reservations_file.exists():
            self.reservations_file.parent.mkdir(exist_ok=True)
            self._save_data({"reservations": [], "last_updated": datetime.now().isoformat()})
    
    def _load_data(self) -> Dict:
        """Load data from storage file."""
        try:
            with open(self.reservations_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.reservations_file}")
            return {"reservations": [], "last_updated": datetime.now().isoformat()}
    
    def _save_data(self, data: Dict):
        """Save data to storage file."""
        with open(self.reservations_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_reservation(self, booking_details: Dict) -> str:
        """Create a new reservation."""
        data = self._load_data()
        
        # Generate unique booking ID
        booking_id = str(uuid.uuid4())
        
        # Add metadata
        booking_details.update({
            "booking_id": booking_id,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed"
        })
        
        # Add to storage
        data["reservations"].append(booking_details)
        data["last_updated"] = datetime.now().isoformat()
        
        self._save_data(data)
        logger.info(f"Created reservation: {booking_id}")
        
        return booking_id
    
    def get_reservation(self, booking_id: str) -> Optional[Dict]:
        """Retrieve a reservation by ID."""
        data = self._load_data()
        
        for reservation in data["reservations"]:
            if reservation["booking_id"] == booking_id:
                return reservation
        
        return None
    
    def update_reservation(self, booking_id: str, updates: Dict) -> bool:
        """Update an existing reservation."""
        data = self._load_data()
        
        for reservation in data["reservations"]:
            if reservation["booking_id"] == booking_id:
                reservation.update(updates)
                reservation["updated_at"] = datetime.now().isoformat()
                data["last_updated"] = datetime.now().isoformat()
                
                self._save_data(data)
                logger.info(f"Updated reservation: {booking_id}")
                return True
        
        return False
    
    def delete_reservation(self, booking_id: str) -> bool:
        """Delete a reservation."""
        data = self._load_data()
        
        initial_length = len(data["reservations"])
        data["reservations"] = [r for r in data["reservations"] if r["booking_id"] != booking_id]
        
        if len(data["reservations"]) < initial_length:
            data["last_updated"] = datetime.now().isoformat()
            self._save_data(data)
            logger.info(f"Deleted reservation: {booking_id}")
            return True
        
        return False
    
    def check_availability(self, check_in: datetime, check_out: datetime, room_type: str) -> bool:
        """Check if a room is available for the given dates."""
        data = self._load_data()
        
        # Simple availability check (can be made more sophisticated)
        for reservation in data["reservations"]:
            if (reservation["room_type"] == room_type and
                datetime.fromisoformat(reservation["check_in_date"]) < check_out and
                datetime.fromisoformat(reservation["check_out_date"]) > check_in):
                return False
        
        return True
    
    def get_all_reservations(self) -> List[Dict]:
        """Get all reservations."""
        data = self._load_data()
        return data["reservations"] 