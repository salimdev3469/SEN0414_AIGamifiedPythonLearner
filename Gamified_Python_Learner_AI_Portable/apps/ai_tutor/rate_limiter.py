"""
Global rate limiter for Gemini API requests
Limits total API requests across all users to prevent quota exhaustion
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Global daily limit for all Gemini API requests
GEMINI_DAILY_LIMIT = 100


def check_gemini_rate_limit():
    """
    Check if we can make a Gemini API request based on daily limit.
    
    Returns:
        tuple: (allowed: bool, remaining: int, reset_time: datetime)
    """
    # Get today's date as string (YYYY-MM-DD)
    today = timezone.now().date().isoformat()
    cache_key = f'gemini_daily_requests_{today}'
    
    # Get current request count
    current_count = cache.get(cache_key, 0)
    
    # Check if limit exceeded
    if current_count >= GEMINI_DAILY_LIMIT:
        # Calculate reset time (midnight tomorrow)
        tomorrow = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        logger.warning(f"Gemini API daily limit ({GEMINI_DAILY_LIMIT}) exceeded. Reset at {tomorrow}")
        return False, 0, tomorrow
    
    # Increment counter
    new_count = current_count + 1
    # Cache until end of day (midnight + 1 day)
    tomorrow = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    seconds_until_midnight = int((tomorrow - timezone.now()).total_seconds())
    cache.set(cache_key, new_count, seconds_until_midnight)
    
    remaining = GEMINI_DAILY_LIMIT - new_count
    logger.info(f"Gemini API request #{new_count}/{GEMINI_DAILY_LIMIT} (remaining: {remaining})")
    
    return True, remaining, tomorrow


def get_gemini_rate_limit_status():
    """
    Get current rate limit status without incrementing counter.
    
    Returns:
        dict: Status with current_count, limit, remaining, reset_time
    """
    today = timezone.now().date().isoformat()
    cache_key = f'gemini_daily_requests_{today}'
    current_count = cache.get(cache_key, 0)
    remaining = max(0, GEMINI_DAILY_LIMIT - current_count)
    tomorrow = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return {
        'current_count': current_count,
        'limit': GEMINI_DAILY_LIMIT,
        'remaining': remaining,
        'reset_time': tomorrow,
        'is_limit_reached': current_count >= GEMINI_DAILY_LIMIT
    }

