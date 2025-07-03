"""
Date parsing utility for extracting dates from user messages.
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import re

class DateParser:
    """Utility class for parsing dates from text."""
    
    @staticmethod
    def extract_dates(text: str) -> Optional[Dict[str, date]]:
        """
        Extract check-in and check-out dates from text.
        
        Args:
            text (str): Text containing date information
            
        Returns:
            Optional[Dict[str, date]]: Dictionary with check_in and check_out dates,
                                     or None if dates couldn't be extracted
        """
        # Common date formats
        date_patterns = [
            # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            # YYYY-MM-DD
            r'(\d{4}-\d{1,2}-\d{1,2})',
            # Month DD, YYYY
            r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            # DD Month YYYY
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            # Tomorrow, next week, etc.
            r'(tomorrow|next week|next month)',
            # X days/weeks from now
            r'(\d+)\s+(day|week|month)s?\s+from\s+(?:now|today)',
        ]
        
        dates = []
        text = text.lower()
        
        # Extract dates using patterns
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                date_str = match.group(1)
                try:
                    # Handle relative dates
                    if date_str == "tomorrow":
                        parsed_date = datetime.now().date() + relativedelta(days=1)
                    elif date_str == "next week":
                        parsed_date = datetime.now().date() + relativedelta(weeks=1)
                    elif date_str == "next month":
                        parsed_date = datetime.now().date() + relativedelta(months=1)
                    elif "from" in match.group(0):
                        # Handle "X days/weeks from now"
                        number = int(match.group(1))
                        unit = match.group(2)
                        if unit == "day":
                            parsed_date = datetime.now().date() + relativedelta(days=number)
                        elif unit == "week":
                            parsed_date = datetime.now().date() + relativedelta(weeks=number)
                        elif unit == "month":
                            parsed_date = datetime.now().date() + relativedelta(months=number)
                    else:
                        # Parse absolute dates
                        parsed_date = parse(date_str).date()
                    
                    dates.append(parsed_date)
                except (ValueError, TypeError):
                    continue
        
        # Sort dates to determine check-in and check-out
        if len(dates) >= 2:
            dates.sort()
            return {
                "check_in": dates[0],
                "check_out": dates[1]
            }
        
        return None
    
    @staticmethod
    def is_valid_date_range(check_in: date, check_out: date) -> Tuple[bool, str]:
        """
        Validate a date range for a hotel booking.
        
        Args:
            check_in (date): Check-in date
            check_out (date): Check-out date
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        today = datetime.now().date()
        
        if check_in < today:
            return False, "Check-in date cannot be in the past"
        
        if check_out <= check_in:
            return False, "Check-out date must be after check-in date"
        
        if (check_out - check_in).days > 30:
            return False, "Maximum stay duration is 30 days"
        
        if (check_in - today).days > 365:
            return False, "Bookings can only be made up to 1 year in advance"
        
        return True, "" 