"""
Date parsing utilities.
"""
from datetime import datetime, timedelta
import re
from typing import Optional, Tuple, Dict
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class DateParser:
    """Date parsing utility class."""
    
    RELATIVE_DATE_PATTERNS = {
        r"today": lambda: datetime.now(),
        r"tomorrow": lambda: datetime.now() + timedelta(days=1),
        r"next week": lambda: datetime.now() + timedelta(weeks=1),
        r"next month": lambda: datetime.now() + relativedelta(months=1),
    }
    
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%B %d, %Y",
        "%d %B %Y",
    ]
    
    @classmethod
    def parse_date_range(cls, text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Parse a date range from text."""
        # Try to find relative dates first
        for pattern, date_func in cls.RELATIVE_DATE_PATTERNS.items():
            if re.search(pattern, text.lower()):
                start_date = date_func()
                # Assume one night stay if no end date specified
                end_date = start_date + timedelta(days=1)
                return start_date, end_date
        
        # Try to find explicit dates
        dates = []
        words = text.split()
        current_date_str = ""
        
        for word in words:
            current_date_str += f" {word}"
            try:
                date = parse(current_date_str.strip(), fuzzy=True)
                dates.append(date)
                current_date_str = ""
            except ValueError:
                continue
        
        if len(dates) >= 2:
            return dates[0], dates[1]
        elif len(dates) == 1:
            return dates[0], dates[0] + timedelta(days=1)
        
        return None, None
    
    @classmethod
    def format_date(cls, date: datetime, format: str = "%Y-%m-%d") -> str:
        """Format a date as string."""
        return date.strftime(format)
    
    @classmethod
    def is_valid_date_range(
        cls,
        start_date: datetime,
        end_date: datetime,
        min_nights: int = 1,
        max_nights: int = 30
    ) -> Tuple[bool, str]:
        """Validate a date range."""
        now = datetime.now()
        
        if start_date < now.replace(hour=0, minute=0, second=0, microsecond=0):
            return False, "Check-in date cannot be in the past"
        
        if end_date <= start_date:
            return False, "Check-out date must be after check-in date"
        
        nights = (end_date - start_date).days
        if nights < min_nights:
            return False, f"Minimum stay is {min_nights} night(s)"
        
        if nights > max_nights:
            return False, f"Maximum stay is {max_nights} nights"
        
        return True, ""
    
    @classmethod
    def get_next_available_dates(
        cls,
        booked_dates: Dict[str, Tuple[datetime, datetime]],
        desired_nights: int = 1,
        start_from: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        """Find next available date range."""
        if start_from is None:
            start_from = datetime.now()
        
        # Sort booked dates
        sorted_bookings = sorted(
            booked_dates.values(),
            key=lambda x: x[0]
        )
        
        current_date = start_from
        for booking_start, booking_end in sorted_bookings:
            # If there's enough gap before this booking
            if (booking_start - current_date).days >= desired_nights:
                return current_date, current_date + timedelta(days=desired_nights)
            current_date = booking_end
        
        # If we get here, return dates after all bookings
        return current_date, current_date + timedelta(days=desired_nights) 