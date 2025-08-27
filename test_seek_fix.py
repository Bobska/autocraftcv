#!/usr/bin/env python3
"""
Test script for SEEK scraping fix - validates JSON content filtering
"""

import os
import django
import sys

# Add the project root to Python path
sys.path.append('c:\\Users\\Dmitry\\OneDrive\\Development\\Copilot\\autocraftcv')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.anti_detection_scraper import SEEKSpecificScraper

def test_json_content_filtering():
    """Test the JSON content filtering functionality"""
    
    scraper = SEEKSpecificScraper()
    
    # Test cases with JSON-encoded content
    test_cases = [
        {
            'name': 'Clean HTML content',
            'input': 'Graduate IT Software Engineer at SDSI',
            'expected_clean': True
        },
        {
            'name': 'JSON-encoded content',
            'input': 'Graduate IT Software Engineer\\u003C\\u002Fstrong\\u003E with SDSI',
            'expected_clean': False  # Should be filtered out
        },
        {
            'name': 'Mixed content',
            'input': 'Graduate IT Software Engineer - \\u003Cstrong\\u003ESDSI is hiring\\u003C\\u002Fstrong\\u003E',
            'expected_clean': False  # Should be filtered out due to high encoding ratio
        },
        {
            'name': 'Normal content with slash',
            'input': 'C# and .NET Framework development',
            'expected_clean': True
        }
    ]
    
    print("🧪 Testing JSON Content Filtering\n")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        
        cleaned = scraper.remove_json_encoded_content(test_case['input'])
        is_clean = len(cleaned.strip()) > 0
        
        print(f"Output: '{cleaned}'")
        print(f"Is Clean: {is_clean}")
        print(f"Expected Clean: {test_case['expected_clean']}")
        
        if is_clean == test_case['expected_clean']:
            print("✅ PASS")
        else:
            print("❌ FAIL")
        
        print("-" * 40)
    
    print("\n🎯 Testing SEEK Data Enhancement")
    print("=" * 60)
    
    # Test SEEK-specific enhancement
    test_job_data = {
        'title': 'Graduate IT Software Engineer',
        'company': 'SDSI',
        'description': '''Kick-Start Your Career as an IT Software Engineer at SDSI – Where Passion Meets Purpose!

Are you a tech-savvy, ambitious recent or soon to be graduate ready to make a real impact? SDSI is looking for talented individuals at the start of their careers to join us in the exciting world of Public Safety, supporting agencies across the globe.

Key Responsibilities:
• Collaborate with SDSI support teams to design and deliver best practice solutions for Public Safety
• Gain expertise in SDSI and Central Square products to provide informed, effective support
• Engage with stakeholders to understand their needs, offering technical solutions that make a difference

What We're Looking For:
• Bachelor's degree in IT
• Skills in .NET Framework, C#, SQL Server, HTML5, CSS, JavaScript, Angular and Flutter
• Experience or strong interest in mobile app development for iOS and Android platforms''',
        'raw_content': 'Some raw content here'
    }
    
    enhanced_data = scraper.enhance_seek_data(test_job_data)
    
    print(f"Title: {enhanced_data['title']}")
    print(f"Company: {enhanced_data['company']}")
    print(f"Site: {enhanced_data['site']}")
    print(f"Country: {enhanced_data['country']}")
    print(f"Description length: {len(enhanced_data['description'])} chars")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_json_content_filtering()
