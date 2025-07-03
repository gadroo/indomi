# Hotel Booking AI Agent

An AI-powered hotel booking system that handles reservations through Instagram DMs. Built with OpenAI, LangChain, and FastAPI.

## Features

- Natural language booking process through Instagram DMs
- Intelligent conversation management with context awareness
- Automated booking, rescheduling, and cancellation
- Hotel information inquiries
- Secure data storage with JSON persistence
- Clean, modular, and maintainable code structure

## Architecture

The system follows clean architecture principles and is organized into the following modules:

- `llm/`: LLM client implementations (OpenAI)
- `models/`: Data models using Pydantic
- `services/`: Business logic and service layer
- `storage/`: Data persistence implementations
- `conversation/`: Conversation flow management
- `prompts/`: Centralized prompt templates
- `utils/`: Utility functions and helpers
- `tests/`: Comprehensive test suite

## Prerequisites

- Python 3.9+
- Instagram Business Account
- OpenAI API Key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hotel-booking-ai.git
   cd hotel-booking-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```

5. Update the `.env` file with your credentials:
   - Add your OpenAI API key
   - Add your Instagram API credentials
   - Configure hotel information

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn src.app:app --reload
   ```

2. The API will be available at `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Project Structure

```
hotel-booking-ai/
├── src/
│   ├── llm/
│   │   ├── base.py
│   │   └── openai_client.py
│   ├── models/
│   │   └── booking.py
│   ├── services/
│   │   ├── base.py
│   │   └── booking.py
│   ├── storage/
│   │   ├── base.py
│   │   └── json_storage.py
│   ├── conversation/
│   │   └── manager.py
│   ├── prompts/
│   │   └── base.py
│   ├── utils/
│   │   └── date_parser.py
│   ├── config.py
│   └── app.py
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_booking.py
│   └── test_conversation.py
├── .env.example
├── requirements.txt
└── README.md
```

## API Endpoints

- `POST /webhook`: Instagram webhook endpoint
- `GET /bookings`: List all bookings
- `GET /bookings/{id}`: Get booking details
- `POST /bookings`: Create a new booking
- `PUT /bookings/{id}`: Update a booking
- `DELETE /bookings/{id}`: Cancel a booking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
