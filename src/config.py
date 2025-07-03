"""
Configuration module for the Hotel Booking AI Agent.
"""
import os
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class Paths(BaseModel):
    """Path configuration."""
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    log_dir: Path = base_dir / "logs"

    def create_directories(self):
        """Create necessary directories."""
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

class APIConfig(BaseModel):
    """API configuration."""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_app_id: str = os.getenv("INSTAGRAM_APP_ID", "")
    instagram_app_secret: str = os.getenv("INSTAGRAM_APP_SECRET", "")

class LLMConfig(BaseModel):
    """LLM configuration."""
    model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

class AppConfig(BaseModel):
    """Application configuration."""
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

class HotelConfig(BaseModel):
    """Hotel configuration."""
    name: str = os.getenv("HOTEL_NAME", "Powersmy Luxury Hotel")
    address: str = os.getenv("HOTEL_ADDRESS", "123 Main Street, Cityville")
    check_in_time: str = os.getenv("CHECK_IN_TIME", "15:00")
    check_out_time: str = os.getenv("CHECK_OUT_TIME", "11:00")
    amenities: list = [
        "Free Wi-Fi",
        "Swimming Pool",
        "Fitness Center",
        "Spa",
        "Restaurant",
        "24/7 Room Service",
        "Business Center",
        "Parking",
    ]
    room_types: Dict[str, str] = {
        "standard": "Standard Room",
        "deluxe": "Deluxe Room",
        "suite": "Executive Suite",
        "presidential": "Presidential Suite",
    }
    policies: Dict[str, str] = {
        "cancellation": "Free cancellation up to 24 hours before check-in",
        "pets": "Pet-friendly hotel with additional cleaning fee",
        "smoking": "Non-smoking property",
        "payment": "Credit card required for reservation",
    }

# Initialize configurations
paths = Paths()
paths.create_directories()

api_config = APIConfig()
llm_config = LLMConfig()
app_config = AppConfig()
hotel_config = HotelConfig()

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    paths.log_dir / "app.log",
    level=app_config.log_level,
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(lambda msg: print(msg), level="INFO", format="{message}")  # Console output

# Export configuration values
OPENAI_API_KEY = api_config.openai_api_key
OPENAI_MODEL = llm_config.model
OPENAI_TEMPERATURE = llm_config.temperature
OPENAI_MAX_TOKENS = llm_config.max_tokens

INSTAGRAM_ACCESS_TOKEN = api_config.instagram_access_token
INSTAGRAM_APP_ID = api_config.instagram_app_id
INSTAGRAM_APP_SECRET = api_config.instagram_app_secret

DEBUG = app_config.debug
LOG_LEVEL = app_config.log_level

MOCK_DATA_FILE = paths.data_dir / "mock_hotel_data.json"
RESERVATIONS_FILE = paths.data_dir / "reservations.json"

HOTEL_CONFIG = hotel_config.dict() 