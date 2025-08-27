#!/usr/bin/env python
"""
Test SEEK selector optimization results
Tests the updated company and description selectors
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.anti_detection_scraper import SEEKSpecificScraper

def test_updated_selectors():
    """Test the updated SEEK selectors"""
    
    # SEEK job URL from previous tests  
    test_url = "https://www.seek.com.au/job/78792139?type=standard&userqueryid=8b49dfb2c71af01b59c5e2c5b7bb2cad-2551651"
    
    print("🔧 Testing Updated SEEK Selectors")
    print("=" * 60)
    print(f"URL: {test_url}")
    print()
    
    # Test with SEEKSpecificScraper
    print("📊 Using SEEKSpecificScraper...")
    scraper = SEEKSpecificScraper()
    
    try:
        job_data, method = scraper.scrape_seek_job(test_url)
        
        print(f"✅ Method: {method}")
        print(f"✅ Title: {job_data.get('title', 'NOT FOUND')}")
        print(f"✅ Company: {job_data.get('company', 'NOT FOUND')}")
        print(f"✅ Location: {job_data.get('location', 'NOT FOUND')}")
        
        description = job_data.get('description', '')
        if description:
            preview = description[:200] + "..." if len(description) > 200 else description
            print(f"✅ Description: {preview}")
        else:
            print(f"❌ Description: NOT FOUND")
            
        print()
        print("🎯 Selector Validation Results:")
        
        # Check if we got the key fields
        if job_data.get('company') and 'NOT FOUND' not in str(job_data.get('company')):
            print("✅ Company extraction: SUCCESS")
        else:
            print("❌ Company extraction: FAILED")
            
        if job_data.get('description') and len(job_data.get('description', '')) > 100:
            print("✅ Description extraction: SUCCESS")
        else:
            print("❌ Description extraction: FAILED")
            
        # Check if JSON filtering worked
        description_text = str(job_data.get('description', ''))
        if '\\u003C' in description_text or '\\u002F' in description_text:
            print("❌ JSON filtering: FAILED (still contains encoded content)")
        else:
            print("✅ JSON filtering: SUCCESS (no encoded content detected)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print()
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_updated_selectors()
