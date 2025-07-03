"""
FastAPI application for the Hotel Booking AI Agent.
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from uuid import UUID

from .config import DEBUG, HOTEL_CONFIG, RESERVATIONS_FILE
from .models.booking import Booking, BookingModification, BookingCancellation
from .services.booking import BookingService
from .storage.json_storage import JSONStorage
from .llm.openai_client import OpenAIClient
from .conversation.manager import ConversationManager
from .instagram.client import InstagramClient

app = FastAPI(
    title="Hotel Booking AI Agent",
    description="AI-powered hotel booking system with Instagram DM integration",
    version="1.0.0",
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_llm_client():
    """Get LLM client instance."""
    return OpenAIClient()

def get_booking_storage():
    """Get booking storage instance."""
    return JSONStorage(RESERVATIONS_FILE, Booking)

def get_booking_service(
    storage: JSONStorage = Depends(get_booking_storage),
    llm_client: OpenAIClient = Depends(get_llm_client)
):
    """Get booking service instance."""
    return BookingService(storage, llm_client)

def get_conversation_manager(
    llm_client: OpenAIClient = Depends(get_llm_client),
    booking_service: BookingService = Depends(get_booking_service)
):
    """Get conversation manager instance."""
    return ConversationManager(llm_client, booking_service)

def get_instagram_client():
    """Get Instagram client instance."""
    return InstagramClient()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hotel Booking AI Agent API",
        "hotel": HOTEL_CONFIG["name"],
        "version": "1.0.0"
    }

@app.get("/webhook")
async def verify_webhook(
    mode: str,
    token: str,
    challenge: str,
    instagram_client: InstagramClient = Depends(get_instagram_client)
):
    """Verify Instagram webhook."""
    if instagram_client.verify_webhook(mode, token, challenge):
        return int(challenge)
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post("/webhook")
async def instagram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature: Optional[str] = Header(None),
    instagram_client: InstagramClient = Depends(get_instagram_client),
    conversation_manager: ConversationManager = Depends(get_conversation_manager)
):
    """Handle Instagram webhook events."""
    # Get raw payload
    payload = await request.body()
    
    # Verify signature
    if not instagram_client.verify_signature(payload, x_hub_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Process webhook data
    data = await request.json()
    message_data = await instagram_client.process_webhook(data)
    
    if not message_data:
        return {"status": "no_action_required"}
    
    # Process message in background
    background_tasks.add_task(
        process_message,
        message_data,
        instagram_client,
        conversation_manager
    )
    
    return {"status": "processing"}

async def process_message(
    message_data: dict,
    instagram_client: InstagramClient,
    conversation_manager: ConversationManager
):
    """Process Instagram message in background."""
    sender_id = message_data["sender_id"]
    message = message_data["message"]
    
    # Mark message as seen
    await instagram_client.mark_seen(sender_id)
    
    # Show typing indicator
    await instagram_client.send_typing_indicator(sender_id, True)
    
    try:
        # Process message through conversation manager
        response = await conversation_manager.handle_message(sender_id, message)
        
        # Send response
        await instagram_client.send_message(sender_id, response)
    except Exception as e:
        # Send error message
        error_message = "I apologize, but I encountered an error processing your request. Please try again."
        await instagram_client.send_message(sender_id, error_message)
    finally:
        # Turn off typing indicator
        await instagram_client.send_typing_indicator(sender_id, False)

@app.get("/bookings", response_model=List[Booking])
async def list_bookings(
    guest_email: Optional[str] = None,
    booking_service: BookingService = Depends(get_booking_service)
):
    """List all bookings, optionally filtered by guest email."""
    filters = {"guest.email": guest_email} if guest_email else None
    return await booking_service.list(filters)

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: UUID,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Get a specific booking by ID."""
    booking = await booking_service.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.post("/bookings", response_model=Booking)
async def create_booking(
    booking_data: dict,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Create a new booking."""
    try:
        return await booking_service.create(booking_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: UUID,
    booking_data: dict,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Update an existing booking."""
    try:
        return await booking_service.update(booking_id, booking_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: UUID,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Delete a booking."""
    if not await booking_service.delete(booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted successfully"}

@app.get("/hotel/info")
async def hotel_info():
    """Get hotel information."""
    return HOTEL_CONFIG

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 