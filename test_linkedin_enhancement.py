#!/usr/bin/env python
"""
Test script for LinkedIn Job Scraping Enhancement
Tests the specific VALE Partners job: https://www.linkedin.com/jobs/view/4280522723/
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.linkedin_scraper import LinkedInJobScraper
from jobassistant.services.scraping_service import JobScrapingService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_linkedin_scraping():
    """Test LinkedIn scraping with the specific VALE Partners job"""
    
    print("=== LinkedIn Scraping Enhancement Test ===")
    print("Testing VALE Partners Junior .NET Developer job")
    
    # The specific job URL that was failing
    test_url = "https://www.linkedin.com/jobs/view/4280522723/"
    
    print(f"\nTesting URL: {test_url}")
    print("\n1. Testing Direct LinkedIn Scraper:")
    print("-" * 50)
    
    try:
        # Test the LinkedIn-specific scraper
        linkedin_scraper = LinkedInJobScraper()
        job_data, method = linkedin_scraper.scrape_linkedin_job(test_url)
        
        print(f"✅ Scraping completed with method: {method}")
        print(f"Quality assessment: {linkedin_scraper.assess_extraction_quality(job_data):.2f}")
        
        # Display extracted data
        print("\nExtracted Data:")
        print(f"📋 Title: {job_data.get('title', 'NOT FOUND')}")
        print(f"🏢 Company: {job_data.get('company', 'NOT FOUND')}")
        print(f"📍 Location: {job_data.get('location', 'NOT FOUND')}")
        print(f"💰 Salary: {job_data.get('salary_range', 'NOT FOUND')}")
        print(f"🏷️ Employment Type: {job_data.get('employment_type', 'NOT FOUND')}")
        
        # Show description length
        description = job_data.get('description', '')
        print(f"📝 Description: {len(description)} characters")
        if description and len(description) > 100:
            print(f"    Preview: {description[:200]}...")
        
        # Show requirements
        requirements = job_data.get('requirements', '')
        print(f"📋 Requirements: {len(requirements)} characters" if requirements else "📋 Requirements: NOT FOUND")
        if requirements and len(requirements) > 50:
            print(f"    Preview: {requirements[:150]}...")
            
        # Show application instructions
        app_instructions = job_data.get('application_instructions', '')
        if app_instructions:
            print(f"📧 Application Instructions: {app_instructions}")
        
        # Check for manual entry requirement
        if job_data.get('requires_manual_entry'):
            print("⚠️ Manual entry required")
            print(f"Reason: {job_data.get('fallback_message', 'Unknown')}")
        
        print("\n" + "="*60)
        
        # Expected vs Actual comparison
        print("2. Results Validation:")
        print("-" * 50)
        
        expected_results = {
            'title': 'Junior .NET Developer',
            'company': 'VALE Partners',
            'location': 'Brisbane City, Queensland, Australia',
            'salary_contains': '$70,000',
            'description_should_contain': ['developer', 'net', '.net', 'sql'],
            'requirements_should_contain': ['experience', 'sql', '.net']
        }
        
        # Validate title
        actual_title = job_data.get('title', '')
        if expected_results['title'].lower() in actual_title.lower():
            print("✅ Title extraction: PASSED")
        else:
            print(f"❌ Title extraction: FAILED (got: {actual_title})")
        
        # Validate company
        actual_company = job_data.get('company', '')
        if expected_results['company'].lower() in actual_company.lower():
            print("✅ Company extraction: PASSED")
        else:
            print(f"❌ Company extraction: FAILED (got: {actual_company})")
        
        # Validate location
        actual_location = job_data.get('location', '')
        if 'brisbane' in actual_location.lower() or 'queensland' in actual_location.lower():
            print("✅ Location extraction: PASSED")
        else:
            print(f"❌ Location extraction: FAILED (got: {actual_location})")
        
        # Validate salary
        actual_salary = job_data.get('salary_range', '')
        if '$70' in actual_salary or '$90' in actual_salary:
            print("✅ Salary extraction: PASSED")
        else:
            print(f"❌ Salary extraction: FAILED (got: {actual_salary})")
        
        # Validate description content
        description_lower = description.lower()
        description_score = sum(1 for term in expected_results['description_should_contain'] if term in description_lower)
        if description_score >= 2:
            print("✅ Description content: PASSED")
        else:
            print(f"❌ Description content: FAILED (found {description_score}/4 expected terms)")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ LinkedIn scraper failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing Integrated Scraping Service:")
    print("-" * 50)
    
    try:
        # Test the integrated scraping service
        scraping_service = JobScrapingService(use_paid_apis=False)
        job_data_integrated, method_integrated = scraping_service.scrape_job(test_url)
        
        print(f"✅ Integrated scraping completed with method: {method_integrated}")
        print(f"📋 Title: {job_data_integrated.get('title', 'NOT FOUND')}")
        print(f"🏢 Company: {job_data_integrated.get('company', 'NOT FOUND')}")
        print(f"📍 Location: {job_data_integrated.get('location', 'NOT FOUND')}")
        
        # Check if manual entry is required
        if job_data_integrated.get('requires_manual_entry'):
            print("⚠️ Integrated service suggests manual entry")
            print(f"Reason: {job_data_integrated.get('fallback_message', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Integrated scraping failed: {str(e)}")
    
    print("\n" + "="*60)
    print("4. Test Summary:")
    print("-" * 50)
    
    print("Expected improvements:")
    print("✅ Company should be 'VALE Partners' (not 'Company Not Available')")
    print("✅ Location should be 'Brisbane City, Queensland, Australia'")
    print("✅ Full job description should be extracted")
    print("✅ Requirements should be extracted (2-5 years experience, .NET 6+, SQL)")
    print("✅ Application instructions should include harold@valepartners.co")
    
    print("\nIf extraction fails due to anti-bot protection:")
    print("✅ Should gracefully fallback to manual entry")
    print("✅ Should provide clear instructions to user")
    print("✅ Should maintain the job URL for manual processing")
    
    print("\n=== LinkedIn Enhancement Test Complete ===")

if __name__ == "__main__":
    test_linkedin_scraping()
