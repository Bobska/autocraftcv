#!/usr/bin/env python3
"""
Test the SEEK scraping fix with the Graduate IT Software Engineer job
"""

import os
import django
import sys

# Add the project root to Python path
sys.path.append('c:\\Users\\Dmitry\\OneDrive\\Development\\Copilot\\autocraftcv')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

def test_seek_scraping():
    """Test SEEK scraping with the Graduate IT Software Engineer job"""
    
    from jobassistant.services.anti_detection_scraper import SEEKSpecificScraper
    
    # URL for the Graduate IT Software Engineer job
    test_url = "https://www.seek.com.au/job/86474131"
    
    print("🧪 Testing SEEK Scraping Fix")
    print("=" * 60)
    print(f"URL: {test_url}")
    print()
    
    scraper = SEEKSpecificScraper()
    
    try:
        print("🔄 Starting scraping...")
        job_data, method = scraper.scrape_seek_job(test_url)
        
        print(f"✅ Scraping completed using method: {method}")
        print()
        
        print("📋 Extracted Data:")
        print("-" * 40)
        
        for field, value in job_data.items():
            if field in ['title', 'company', 'location', 'description']:
                if value:
                    print(f"**{field.upper()}:** {value[:200]}{'...' if len(str(value)) > 200 else ''}")
                else:
                    print(f"**{field.upper()}:** (not extracted)")
                print()
        
        # Check for JSON-encoded artifacts
        print("🔍 Checking for JSON-encoded content:")
        print("-" * 40)
        
        json_artifacts = ['\\u003C', '\\u002F', '\u003C', '\u002F']
        found_artifacts = []
        
        for field in ['title', 'company', 'description']:
            if job_data.get(field):
                for artifact in json_artifacts:
                    if artifact in str(job_data[field]):
                        found_artifacts.append(f"{field}: {artifact}")
        
        if found_artifacts:
            print("❌ JSON-encoded artifacts found:")
            for artifact in found_artifacts:
                print(f"  - {artifact}")
        else:
            print("✅ No JSON-encoded artifacts found!")
        
        print()
        print("🎯 Summary:")
        print("-" * 40)
        print(f"Method: {method}")
        print(f"Manual entry required: {job_data.get('manual_entry_required', False)}")
        print(f"Title extracted: {'Yes' if job_data.get('title') else 'No'}")
        print(f"Company extracted: {'Yes' if job_data.get('company') else 'No'}")
        print(f"Description extracted: {'Yes' if job_data.get('description') else 'No'}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {str(e)}")

if __name__ == "__main__":
    test_seek_scraping()
