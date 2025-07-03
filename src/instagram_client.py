"""
Instagram integration module for the Hotel Booking AI Agent.
"""
from typing import Dict, List, Optional
import json
import requests
from datetime import datetime
from loguru import logger
from config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
)

class InstagramClient:
    """Handles Instagram API integration."""
    
    def __init__(self):
        """Initialize the Instagram client."""
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.app_id = INSTAGRAM_APP_ID
        self.app_secret = INSTAGRAM_APP_SECRET
        self.base_url = "https://graph.instagram.com/v12.0"
        
        if not all([self.access_token, self.app_id, self.app_secret]):
            logger.warning("Instagram credentials not fully configured")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make an API request to Instagram."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API error: {str(e)}")
            raise
    
    async def send_message(self, user_id: str, message: str) -> bool:
        """Send a message to a user."""
        try:
            endpoint = "me/messages"
            data = {
                "recipient": {"id": user_id},
                "message": {"text": message}
            }
            
            response = self._make_request(endpoint, method="POST", data=data)
            logger.info(f"Message sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {user_id}: {str(e)}")
            return False
    
    async def get_messages(self, user_id: str) -> List[Dict]:
        """Get messages from a specific user."""
        try:
            endpoint = f"me/conversations/{user_id}/messages"
            response = self._make_request(endpoint)
            
            messages = response.get("data", [])
            logger.info(f"Retrieved {len(messages)} messages from user {user_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages from {user_id}: {str(e)}")
            return []
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify Instagram webhook."""
        if mode == "subscribe" and token == self.app_secret:
            return challenge
        return None
    
    def process_webhook(self, data: Dict) -> Optional[Dict]:
        """Process incoming webhook data."""
        try:
            entry = data.get("entry", [{}])[0]
            messaging = entry.get("messaging", [{}])[0]
            
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {}).get("text")
            
            if sender_id and message:
                logger.info(f"Received message from {sender_id}: {message}")
                return {
                    "sender_id": sender_id,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return None 