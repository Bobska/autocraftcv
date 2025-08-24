#!/usr/bin/env python
"""
LinkedIn Bypass Scraper Test Script
Tests the new LinkedIn authentication bypass functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

import logging
from jobassistant.services.linkedin_bypass_scraper import LinkedInBypassScraper
from jobassistant.services.scraping_service import JobScrapingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_linkedin_bypass():
    """Test LinkedIn bypass functionality with example URL"""
    
    # Test URL - replace with actual LinkedIn job URL
    test_url = "https://www.linkedin.com/jobs/view/4280522723"
    
    print("=" * 60)
    print("LinkedIn Bypass Scraper Test")
    print("=" * 60)
    print(f"Testing URL: {test_url}")
    print()
    
    # Test 1: Direct bypass scraper
    print("Test 1: Direct LinkedInBypassScraper")
    print("-" * 40)
    
    try:
        bypass_scraper = LinkedInBypassScraper()
        job_data, method = bypass_scraper.scrape_linkedin_job(test_url)
        
        print(f"Method used: {method}")
        print(f"Title: {job_data.get('title', 'Not found')}")
        print(f"Company: {job_data.get('company', 'Not found')}")
        print(f"Location: {job_data.get('location', 'Not found')}")
        print(f"Requires manual entry: {job_data.get('requires_manual_entry', False)}")
        
        if job_data.get('description'):
            print(f"Description preview: {job_data['description'][:200]}...")
        
        print(f"Bypass successful: {not job_data.get('requires_manual_entry', True)}")
        
    except Exception as e:
        print(f"Direct bypass test failed: {e}")
    
    print()
    
    # Test 2: Through main scraping service
    print("Test 2: Through JobScrapingService")
    print("-" * 40)
    
    try:
        scraper = JobScrapingService()
        job_data, method = scraper.scrape_job(test_url)
        
        print(f"Method used: {method}")
        print(f"Title: {job_data.get('title', 'Not found')}")
        print(f"Company: {job_data.get('company', 'Not found')}")
        print(f"Location: {job_data.get('location', 'Not found')}")
        print(f"Requires manual entry: {job_data.get('requires_manual_entry', False)}")
        
        if job_data.get('bypass_attempted'):
            print("✓ Bypass methods were attempted")
        
        print(f"Overall success: {not job_data.get('requires_manual_entry', True)}")
        
    except Exception as e:
        print(f"Main scraper test failed: {e}")
    
    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)

def test_individual_bypass_methods():
    """Test individual bypass methods"""
    
    test_url = "https://www.linkedin.com/jobs/view/4280522723"
    
    print("Testing Individual Bypass Methods")
    print("=" * 50)
    
    bypass_scraper = LinkedInBypassScraper()
    
    # Test mobile version
    print("1. Testing mobile version bypass...")
    try:
        job_data, method = bypass_scraper._method_mobile_version(test_url, "4280522723")
        print(f"   Mobile bypass: {'SUCCESS' if job_data.get('title') else 'FAILED'}")
        if job_data.get('title'):
            print(f"   Title: {job_data['title']}")
    except Exception as e:
        print(f"   Mobile bypass: FAILED - {e}")
    
    # Test requests bypass
    print("2. Testing requests bypass...")
    try:
        job_data, method = bypass_scraper._method_requests_bypass(test_url, "4280522723")
        print(f"   Requests bypass: {'SUCCESS' if job_data.get('title') else 'FAILED'}")
        if job_data.get('title'):
            print(f"   Title: {job_data['title']}")
    except Exception as e:
        print(f"   Requests bypass: FAILED - {e}")
    
    # Test Google cache
    print("3. Testing Google cache bypass...")
    try:
        job_data, method = bypass_scraper._method_google_cache(test_url, "4280522723")
        print(f"   Google cache: {'SUCCESS' if job_data.get('title') else 'FAILED'}")
        if job_data.get('title'):
            print(f"   Title: {job_data['title']}")
    except Exception as e:
        print(f"   Google cache: FAILED - {e}")
    
    print("Individual method testing completed!")

if __name__ == "__main__":
    print("LinkedIn Bypass Functionality Test")
    print("=" * 50)
    
    try:
        test_linkedin_bypass()
        print()
        test_individual_bypass_methods()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
