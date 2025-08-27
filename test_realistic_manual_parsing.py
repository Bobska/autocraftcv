#!/usr/bin/env python
"""
Test manual entry with realistic mixed content
Tests that manual entry properly extracts clean content while filtering JSON artifacts
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.ai_content_parser import AIJobContentParser

def test_realistic_content():
    """Test with realistic content that has some JSON contamination"""
    
    print("🧪 Testing Realistic Mixed Content")
    print("=" * 60)
    
    # More realistic content with some JSON artifacts (like what users actually encounter)
    mixed_content = """
    Graduate IT Software Engineer
    TechCorp Solutions
    East Brisbane, Brisbane QLD

    About the Role:
    We are seeking a passionate Graduate IT Software Engineer to join our dynamic team. 
    This is an excellent opportunity to kick-start your career in software development 
    while working on cutting-edge projects.

    Key Responsibilities:
    • Develop and maintain software applications
    • Collaborate with senior developers on complex projects  
    • Participate in code reviews and testing
    • \\u003Cspan\\u003EHidden JSON content\\u003C\\u002Fspan\\u003E
    • Learn new technologies and frameworks

    Requirements:
    • Bachelor's degree in Computer Science, IT, or related field
    • Strong programming skills in Java, Python, or C#
    • Understanding of software development lifecycle
    • Excellent problem-solving abilities
    • Strong communication skills

    What We Offer:
    • Competitive salary package  
    • Professional development opportunities
    • Flexible working arrangements
    • Great team culture

    Location: East Brisbane, Brisbane QLD
    Employment Type: Full-time
    Salary: $65,000 - $75,000 per annum

    Apply now to begin your journey with TechCorp Solutions!
    """
    
    print("📄 Content Analysis:")
    print(f"Length: {len(mixed_content)} characters")
    print("JSON artifacts present:", "\\u003C" in mixed_content)
    print("Clean content dominates:", mixed_content.count('\\u') < 10)
    print()
    
    # Test the AI parser
    parser = AIJobContentParser()
    result = parser.parse_job_content(mixed_content)
    
    print("🎯 Parsing Results:")
    print(f"✅ Title: {result.get('title', 'NOT FOUND')}")
    print(f"✅ Company: {result.get('company', 'NOT FOUND')}")
    print(f"✅ Location: {result.get('location', 'NOT FOUND')}")
    
    description = result.get('description', '')
    if description and len(description) > 50:
        preview = description[:200] + "..." if len(description) > 200 else description
        print(f"✅ Description: {preview}")
    else:
        print(f"❌ Description: {description}")
    
    requirements = result.get('requirements', '')
    if requirements and len(requirements) > 50:
        req_preview = requirements[:200] + "..." if len(requirements) > 200 else requirements
        print(f"✅ Requirements: {req_preview}")
    else:
        print(f"❌ Requirements: {requirements}")
    
    print()
    print("🔍 Content Quality Check:")
    
    # Check for specific expected content
    expected_content = [
        ("Graduate IT Software Engineer", result.get('title', '')),
        ("TechCorp Solutions", result.get('company', '')),
        ("East Brisbane", result.get('location', '')),
        ("Bachelor's degree", result.get('requirements', '')),
        ("software development", result.get('description', ''))
    ]
    
    for expected, actual in expected_content:
        if expected.lower() in actual.lower():
            print(f"✅ Found expected content: '{expected}'")
        else:
            print(f"❌ Missing expected content: '{expected}' in {actual[:50]}...")
    
    # Check that JSON artifacts were removed
    all_content = ' '.join([
        result.get('title', ''),
        result.get('company', ''), 
        result.get('location', ''),
        result.get('description', ''),
        result.get('requirements', '')
    ])
    
    if '\\u003C' not in all_content and '\\u002F' not in all_content:
        print("✅ JSON artifacts successfully filtered out")
    else:
        print("❌ JSON artifacts still present in results")
    
    print()
    print("📊 Final Assessment:")
    quality = result.get('extraction_quality', 'unknown')
    print(f"✅ Extraction Quality: {quality}")
    
    ai_parsed = result.get('ai_parsed', False)
    print(f"✅ AI Parsing Used: {ai_parsed}")
    
    needs_review = result.get('needs_review', False)
    print(f"✅ Needs Review: {needs_review}")
    
    print()
    print("🏁 Test Complete!")
    
    # Overall success check
    success_criteria = [
        result.get('title') and 'Graduate' in result.get('title', ''),
        result.get('company') and 'TechCorp' in result.get('company', ''),
        '\\u003C' not in all_content,
        quality in ['good', 'excellent']
    ]
    
    if all(success_criteria):
        print("🎉 SUCCESS: Manual entry parsing is working correctly!")
        print("   - Extracts clean content properly")
        print("   - Filters out JSON contamination") 
        print("   - Maintains high quality parsing")
    else:
        print("⚠️ NEEDS ATTENTION: Some parsing issues detected")

if __name__ == "__main__":
    test_realistic_content()
