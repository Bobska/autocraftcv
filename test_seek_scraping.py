#!/usr/bin/env python
"""
Test script for SEEK anti-detection scraping
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.anti_detection_scraper import AntiDetectionScraper, SEEKSpecificScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_seek_scraping():
    """Test SEEK scraping with anti-detection"""
    
    # Example SEEK URLs (these are just for testing - replace with real ones)
    test_urls = [
        "https://www.seek.com.au/job/58234567",  # Example URL format
        "https://www.seek.com.au/software-developer-jobs",  # Search page
    ]
    
    print("=== Testing SEEK Anti-Detection Scraping ===")
    
    # Test general anti-detection scraper
    print("\n1. Testing General Anti-Detection Scraper:")
    scraper = AntiDetectionScraper()
    
    # Test with a real job posting URL if available
    test_url = "https://www.seek.com.au/"  # Start with main page
    
    try:
        job_data, method = scraper.scrape_protected_site(test_url)
        print(f"✅ General scraper result: {method}")
        print(f"Data keys: {list(job_data.keys()) if job_data else 'No data'}")
        
        if job_data.get('title'):
            print(f"Title: {job_data['title'][:100]}...")
        if job_data.get('company'):
            print(f"Company: {job_data['company'][:50]}...")
            
    except Exception as e:
        print(f"❌ General scraper error: {str(e)}")
    
    # Test SEEK-specific scraper
    print("\n2. Testing SEEK-Specific Scraper:")
    seek_scraper = SEEKSpecificScraper()
    
    try:
        job_data, method = seek_scraper.scrape_seek_job(test_url)
        print(f"✅ SEEK scraper result: {method}")
        print(f"Data keys: {list(job_data.keys()) if job_data else 'No data'}")
        
        if job_data.get('title'):
            print(f"Title: {job_data['title'][:100]}...")
        if job_data.get('company'):
            print(f"Company: {job_data['company'][:50]}...")
            
    except Exception as e:
        print(f"❌ SEEK scraper error: {str(e)}")
    
    print("\n=== Test Complete ===")
    print("\nNote: For actual job posting scraping, provide a real SEEK job URL")
    print("Example: https://www.seek.com.au/job/58234567")

if __name__ == "__main__":
    test_seek_scraping()
