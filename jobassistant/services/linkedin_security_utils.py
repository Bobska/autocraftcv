"""
Enhanced Security and Error Handling Improvements for LinkedIn Session Scraper
"""

from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class LinkedInScrapingError(Exception):
    """Custom exception for LinkedIn scraping errors"""
    pass


class AuthenticationError(LinkedInScrapingError):
    """Raised when LinkedIn authentication fails"""
    pass


class RateLimitError(LinkedInScrapingError):
    """Raised when LinkedIn rate limiting is detected"""
    pass


@contextmanager
def safe_driver_operation(driver):
    """Context manager for safe driver operations"""
    if driver is None:
        raise LinkedInScrapingError("Driver not initialized")
    
    try:
        yield driver
    except Exception as e:
        logger.error(f"Driver operation failed: {e}")
        raise LinkedInScrapingError(f"Driver operation failed: {e}")


class SecureCredentialManager:
    """Secure credential management for LinkedIn authentication"""
    
    @staticmethod
    def validate_credentials(email: str, password: str) -> bool:
        """Validate LinkedIn credentials format"""
        if not email or not password:
            return False
        
        # Basic email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False
        
        # Password strength validation
        if len(password) < 6:
            return False
        
        return True
    
    @staticmethod
    def sanitize_session_data(session_data: dict) -> dict:
        """Sanitize session data before storage"""
        # Remove sensitive fields that shouldn't be stored
        sensitive_fields = ['password', 'credit_card', 'ssn', 'api_key']
        
        sanitized = {}
        for key, value in session_data.items():
            if key.lower() not in sensitive_fields:
                sanitized[key] = value
        
        return sanitized


class PerformanceOptimizer:
    """Performance optimization utilities for scraping"""
    
    @staticmethod
    def is_element_ready(driver, selector: str, timeout: int = 10) -> bool:
        """Check if element is ready for interaction"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element is not None
        except:
            return False
    
    @staticmethod
    def optimize_driver_settings(options):
        """Optimize Chrome driver settings for better performance"""
        # Performance optimizations
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')  # Only if JS not needed
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        return options
