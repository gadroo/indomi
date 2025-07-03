"""
Instagram client implementation.
"""
from typing import Dict, Any, Optional
import hmac
import hashlib
import json
import httpx
from loguru import logger

from ..config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_VERIFY_TOKEN,
    INSTAGRAM_API_VERSION
)

class InstagramClient:
    """Instagram client for handling DM interactions."""
    
    def __init__(self):
        """Initialize Instagram client."""
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.app_secret = INSTAGRAM_APP_SECRET
        self.verify_token = INSTAGRAM_VERIFY_TOKEN
        self.api_version = INSTAGRAM_API_VERSION
        self.base_url = f"https://graph.facebook.com/v{self.api_version}"
        self.client = httpx.AsyncClient()
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> bool:
        """Verify webhook subscription."""
        if mode == "subscribe" and token == self.verify_token:
            return True
        return False
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook payload signature."""
        expected_sig = hmac.new(
            self.app_secret.encode('utf-8'),
            payload,
            hashlib.sha1
        ).hexdigest()
        return hmac.compare_digest(f"sha1={expected_sig}", signature)
    
    async def process_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process webhook payload."""
        try:
            # Extract messaging events
            entry = data.get("entry", [{}])[0]
            messaging = entry.get("messaging", [{}])[0]
            
            # Check if it's a message event
            if "message" not in messaging:
                return None
            
            return {
                "sender_id": messaging["sender"]["id"],
                "recipient_id": messaging["recipient"]["id"],
                "message": messaging["message"].get("text", ""),
                "timestamp": messaging.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
            return None
    
    async def send_message(self, recipient_id: str, message: str) -> bool:
        """Send a message to a user."""
        try:
            url = f"{self.base_url}/me/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
                "messaging_type": "RESPONSE"
            }
            params = {"access_token": self.access_token}
            
            async with self.client as client:
                response = await client.post(url, json=payload, params=params)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            url = f"{self.base_url}/{user_id}"
            params = {
                "access_token": self.access_token,
                "fields": "name,profile_pic"
            }
            
            async with self.client as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None
    
    async def mark_seen(self, recipient_id: str) -> bool:
        """Mark message as seen."""
        try:
            url = f"{self.base_url}/me/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "sender_action": "mark_seen"
            }
            params = {"access_token": self.access_token}
            
            async with self.client as client:
                response = await client.post(url, json=payload, params=params)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error marking message as seen: {str(e)}")
            return False
    
    async def send_typing_indicator(self, recipient_id: str, on: bool = True) -> bool:
        """Send typing indicator."""
        try:
            url = f"{self.base_url}/me/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "sender_action": "typing_on" if on else "typing_off"
            }
            params = {"access_token": self.access_token}
            
            async with self.client as client:
                response = await client.post(url, json=payload, params=params)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error sending typing indicator: {str(e)}")
            return False 