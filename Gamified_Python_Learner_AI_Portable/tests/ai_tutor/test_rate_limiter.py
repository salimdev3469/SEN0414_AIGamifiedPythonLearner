"""
Tests for AI Tutor rate limiter
"""
import pytest
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from apps.ai_tutor.rate_limiter import (
    check_gemini_rate_limit,
    get_gemini_rate_limit_status,
    GEMINI_DAILY_LIMIT
)


@pytest.mark.unit
@pytest.mark.django_db
class TestGeminiRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limit_allows_request_when_under_limit(self):
        """Test that requests are allowed when under limit"""
        # Clear cache
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.delete(cache_key)
        
        allowed, remaining, reset_time = check_gemini_rate_limit()
        
        assert allowed is True
        assert remaining == GEMINI_DAILY_LIMIT - 1
        assert isinstance(reset_time, timezone.datetime)
    
    def test_rate_limit_blocks_when_limit_reached(self):
        """Test that requests are blocked when limit is reached"""
        # Set count to limit
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.set(cache_key, GEMINI_DAILY_LIMIT, 86400)
        
        allowed, remaining, reset_time = check_gemini_rate_limit()
        
        assert allowed is False
        assert remaining == 0
        assert isinstance(reset_time, timezone.datetime)
    
    def test_rate_limit_increments_counter(self):
        """Test that counter increments with each request"""
        # Clear cache
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.delete(cache_key)
        
        # First request
        allowed1, remaining1, _ = check_gemini_rate_limit()
        count1 = cache.get(cache_key, 0)
        
        # Second request
        allowed2, remaining2, _ = check_gemini_rate_limit()
        count2 = cache.get(cache_key, 0)
        
        assert allowed1 is True
        assert allowed2 is True
        assert count2 == count1 + 1
        assert remaining2 == remaining1 - 1
    
    def test_get_rate_limit_status(self):
        """Test getting rate limit status without incrementing"""
        # Clear cache
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.delete(cache_key)
        
        status = get_gemini_rate_limit_status()
        
        assert status['current_count'] == 0
        assert status['limit'] == GEMINI_DAILY_LIMIT
        assert status['remaining'] == GEMINI_DAILY_LIMIT
        assert status['is_limit_reached'] is False
        assert isinstance(status['reset_time'], timezone.datetime)
    
    def test_get_rate_limit_status_when_limit_reached(self):
        """Test status when limit is reached"""
        # Set count to limit
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.set(cache_key, GEMINI_DAILY_LIMIT, 86400)
        
        status = get_gemini_rate_limit_status()
        
        assert status['current_count'] == GEMINI_DAILY_LIMIT
        assert status['remaining'] == 0
        assert status['is_limit_reached'] is True
    
    def test_rate_limit_resets_daily(self):
        """Test that rate limit uses daily cache keys"""
        today = timezone.now().date().isoformat()
        cache_key = f'gemini_daily_requests_{today}'
        cache.set(cache_key, 50, 86400)
        
        status = get_gemini_rate_limit_status()
        
        assert status['current_count'] == 50
        assert status['remaining'] == GEMINI_DAILY_LIMIT - 50

