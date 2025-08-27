#!/usr/bin/env python
"""
Test manual entry JSON filtering
Tests that manual entry properly filters JSON-encoded content
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

def test_json_filtering():
    """Test JSON filtering in manual entry"""
    
    print("🧪 Testing Manual Entry JSON Filtering")
    print("=" * 60)
    
    # Sample content with JSON-encoded contamination (like what users might copy from SEEK)
    contaminated_content = """
    Graduate IT Software Engineer
    TechCorp Solutions
    East Brisbane, Brisbane QLD
    
    Job description with normal content but also contains JSON artifacts:
    \\u003Cdiv\\u003E This should be filtered out \\u003C\\u002Fdiv\\u003E
    
    We are looking for a talented Graduate IT Software Engineer to join our team.
    You will work on exciting projects and develop your skills.
    
    Requirements:
    - Bachelor's degree in Computer Science
    - Knowledge of programming languages
    - \\u003Cscript\\u003Evar jobData = {\\u0022title\\u0022: \\u0022Graduate IT\\u0022}\\u003C\\u002Fscript\\u003E
    
    This is a great opportunity to start your career in technology.
    """
    
    print("📄 Original Content (showing JSON contamination):")
    print(f"Length: {len(contaminated_content)} characters")
    print("JSON artifacts present:", "\\u003C" in contaminated_content)
    print()
    
    # Test the AI parser
    parser = AIJobContentParser()
    result = parser.parse_job_content(contaminated_content)
    
    print("🎯 Parsing Results:")
    print(f"✅ Title: {result.get('title', 'NOT FOUND')}")
    print(f"✅ Company: {result.get('company', 'NOT FOUND')}")
    print(f"✅ Location: {result.get('location', 'NOT FOUND')}")
    
    description = result.get('description', '')
    if description:
        preview = description[:150] + "..." if len(description) > 150 else description
        print(f"✅ Description: {preview}")
    else:
        print("❌ Description: NOT FOUND")
    
    requirements = result.get('requirements', '')
    if requirements:
        req_preview = requirements[:150] + "..." if len(requirements) > 150 else requirements
        print(f"✅ Requirements: {req_preview}")
    else:
        print("❌ Requirements: NOT FOUND")
    
    print()
    print("🔍 JSON Filtering Validation:")
    
    # Check if JSON artifacts were removed from each field
    all_fields = [
        result.get('title', ''),
        result.get('company', ''),
        result.get('location', ''),
        result.get('description', ''),
        result.get('requirements', '')
    ]
    
    json_contamination_found = False
    for field_name, field_value in [
        ('title', result.get('title', '')),
        ('company', result.get('company', '')),
        ('location', result.get('location', '')),
        ('description', result.get('description', '')),
        ('requirements', result.get('requirements', ''))
    ]:
        if '\\u003C' in field_value or '\\u002F' in field_value:
            print(f"❌ JSON contamination found in {field_name}: {field_value[:100]}...")
            json_contamination_found = True
    
    if not json_contamination_found:
        print("✅ No JSON contamination detected in any field")
    
    print()
    print("📊 Quality Assessment:")
    quality = result.get('extraction_quality', 'unknown')
    print(f"✅ Extraction Quality: {quality}")
    
    ai_parsed = result.get('ai_parsed', False)
    print(f"✅ AI Parsing Used: {ai_parsed}")
    
    needs_review = result.get('needs_review', False)
    print(f"✅ Needs Review: {needs_review}")
    
    print()
    print("🏁 Test Complete!")
    
    # Summary
    if not json_contamination_found and quality != 'poor':
        print("🎉 SUCCESS: JSON filtering is working correctly!")
    else:
        print("⚠️ ISSUE: JSON filtering may need adjustment")

if __name__ == "__main__":
    test_json_filtering()
