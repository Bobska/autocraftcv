#!/usr/bin/env python
"""
Test script for AI Job Content Parser
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.services.ai_content_parser import AIJobContentParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_parsing():
    """Test AI-powered job content parsing"""
    
    print("=== Testing AI Job Content Parser ===")
    
    # Sample job posting content
    sample_content = """
    Senior Software Engineer - Python/Django
    TechCorp Australia
    Sydney, NSW
    
    We are seeking a talented Senior Software Engineer to join our growing team. 
    
    About the Role:
    - Design and develop scalable web applications using Python and Django
    - Collaborate with cross-functional teams to deliver high-quality software
    - Mentor junior developers and contribute to technical decisions
    
    Requirements:
    - 5+ years of experience in Python development
    - Strong knowledge of Django framework
    - Experience with PostgreSQL and Redis
    - Familiarity with AWS or other cloud platforms
    - Bachelor's degree in Computer Science or related field
    
    What we offer:
    - Competitive salary package ($120k - $150k)
    - Flexible working arrangements
    - Professional development opportunities
    - Health and wellness benefits
    
    Apply now to join our innovative team!
    """
    
    parser = AIJobContentParser()
    
    try:
        print("\n1. Testing content parsing...")
        parsed_data = parser.parse_job_content(sample_content)
        
        print(f"✅ Parsing successful!")
        print(f"Title: {parsed_data.get('title', 'N/A')}")
        print(f"Company: {parsed_data.get('company', 'N/A')}")
        print(f"Location: {parsed_data.get('location', 'N/A')}")
        print(f"Salary: {parsed_data.get('salary_range', 'N/A')}")
        print(f"Description length: {len(parsed_data.get('description', ''))}")
        print(f"Requirements length: {len(parsed_data.get('requirements', ''))}")
        
        print("\n2. Testing with URL content...")
        url_content = """
        https://www.seek.com.au/job/58234567
        
        Full Stack Developer
        InnovateTech Solutions
        Melbourne, Victoria
        
        Join our dynamic team as a Full Stack Developer...
        """
        
        parsed_url_data = parser.parse_job_content(url_content)
        print(f"✅ URL parsing successful!")
        print(f"Title: {parsed_url_data.get('title', 'N/A')}")
        print(f"Company: {parsed_url_data.get('company', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Parsing error: {str(e)}")
    
    print("\n=== AI Parser Test Complete ===")

if __name__ == "__main__":
    test_ai_parsing()
