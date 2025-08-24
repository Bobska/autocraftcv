"""
Utility functions for safe job data handling and database operations
"""

import re
from typing import Dict, Any, Optional


def clean_job_data(raw_data: Dict[str, Any], job_url: str) -> Dict[str, Any]:
    """
    Clean and validate job data before database save.
    Ensures all fields have safe default values to prevent NOT NULL constraint errors.
    """
    
    # Extract and clean each field with safe defaults
    cleaned = {
        'title': safe_extract_field(raw_data, 'title', 'Job Title Not Available'),
        'company': safe_extract_field(raw_data, 'company', 'Company Not Available'),
        'location': safe_extract_field(raw_data, 'location', 'Location Not Available'),
        'description': safe_extract_field(raw_data, 'description', 'Job description not extracted'),
        'requirements': safe_extract_field(raw_data, 'requirements', ''),
        'qualifications': safe_extract_field(raw_data, 'qualifications', ''),
        'responsibilities': safe_extract_field(raw_data, 'responsibilities', ''),
        'salary_range': safe_extract_field(raw_data, ['salary', 'salary_range', 'salary_info'], ''),
        'employment_type': safe_extract_field(raw_data, 'employment_type', ''),
        'application_instructions': safe_extract_field(raw_data, 'application_instructions', ''),
        'raw_content': safe_extract_field(raw_data, 'raw_content', ''),
        'scraping_method': safe_extract_field(raw_data, 'scraping_method', 'enhanced_scraping'),
        'extraction_method': safe_extract_field(raw_data, 'extraction_method', 'standard'),
        'site_domain': extract_domain_from_url(job_url),
        'needs_review': raw_data.get('needs_review', False)
    }
    
    # Additional validation to ensure no None values
    for key, value in cleaned.items():
        if value is None:
            if key in ['title', 'company', 'location']:
                cleaned[key] = f'{key.replace("_", " ").title()} Not Available'
            else:
                cleaned[key] = ''
    
    # Validate critical fields
    validate_critical_fields(cleaned)
    
    return cleaned


def safe_extract_field(raw_data: Dict[str, Any], field_names: Any, default_value: str = '') -> str:
    """
    Safely extract a field from raw data with multiple possible field names.
    Returns default_value if field is missing, None, or empty.
    """
    
    # Handle single field name or list of field names
    if isinstance(field_names, str):
        field_names = [field_names]
    
    # Try each field name
    for field_name in field_names:
        value = raw_data.get(field_name)
        
        if value is not None:
            # Clean the value
            if isinstance(value, str):
                cleaned_value = value.strip()
                if cleaned_value:  # Not empty after stripping
                    return cleaned_value
            else:
                # Non-string value, convert to string
                str_value = str(value).strip()
                if str_value and str_value.lower() not in ['none', 'null', 'undefined']:
                    return str_value
    
    # No valid value found, return default
    return default_value


def validate_critical_fields(cleaned_data: Dict[str, Any]) -> None:
    """
    Validate that critical fields meet minimum requirements.
    Raises ValueError if validation fails.
    """
    
    # Ensure title is meaningful
    title = cleaned_data.get('title', '')
    if not title or len(title.strip()) < 3:
        cleaned_data['title'] = 'Job Title Not Available'
    
    # Ensure company is meaningful
    company = cleaned_data.get('company', '')
    if not company or len(company.strip()) < 2:
        cleaned_data['company'] = 'Company Not Available'
    
    # Ensure location exists (key fix for constraint error)
    location = cleaned_data.get('location', '')
    if not location or len(location.strip()) < 2:
        cleaned_data['location'] = 'Location Not Available'
    
    # Validate URL exists
    if 'url' in cleaned_data and not cleaned_data['url']:
        raise ValueError("Job URL is required")


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL for site_domain field"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return 'unknown'


def enhance_location_extraction(page_text: str, soup=None, driver=None) -> str:
    """
    Enhanced location extraction with multiple fallback strategies.
    Specifically designed to prevent location NOT NULL constraint errors.
    """
    
    # Strategy 1: CSS selectors for location (if soup or driver available)
    if soup or driver:
        location_selectors = [
            '[data-test="job-location"]',
            '.jobs-unified-top-card__bullet',
            '.job-criteria__text',
            '.jobs-details-top-card__bullet',
            '.jobs-unified-top-card__primary-description',
            '.job-details-top-card__job-insight',
            'span:contains("Australia")',
            'span:contains("Sydney")',
            'span:contains("Melbourne")',
            'span:contains("Brisbane")',
            'span:contains("Perth")',
            'span:contains("Adelaide")',
        ]
        
        for selector in location_selectors:
            try:
                if driver:  # Selenium
                    from selenium.webdriver.common.by import By
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    location_text = element.text.strip()
                else:  # BeautifulSoup
                    element = soup.select_one(selector)
                    location_text = element.get_text().strip() if element else ''
                
                if location_text and is_valid_location(location_text):
                    return location_text
            except:
                continue
    
    # Strategy 2: Text pattern matching for Australian locations
    if page_text:
        location_patterns = [
            # Australian cities with state/country
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*(?:Australia|NSW|QLD|VIC|WA|SA|TAS|NT|ACT|New South Wales|Queensland|Victoria|Western Australia|South Australia|Tasmania|Northern Territory|Australian Capital Territory))',
            # Major Australian cities
            r'(Sydney|Melbourne|Brisbane|Perth|Adelaide|Darwin|Hobart|Canberra)(?:\s*,\s*(?:Australia|NSW|QLD|VIC|WA|SA|TAS|NT|ACT))?',
            # Work arrangements
            r'(Remote|Hybrid|Work from home)',
            # City, State pattern
            r'([A-Z][a-z]+\s+City,\s*[A-Z][a-z]+)',
            # General location patterns
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                location_text = match.group(1).strip()
                if is_valid_location(location_text):
                    return location_text
    
    # Strategy 3: Look for common location indicators
    if page_text:
        location_indicators = [
            'brisbane', 'sydney', 'melbourne', 'perth', 'adelaide', 'darwin', 'hobart', 'canberra',
            'queensland', 'new south wales', 'victoria', 'western australia', 'south australia',
            'tasmania', 'northern territory', 'australian capital territory',
            'nsw', 'qld', 'vic', 'wa', 'sa', 'tas', 'nt', 'act'
        ]
        
        page_lower = page_text.lower()
        for indicator in location_indicators:
            if indicator in page_lower:
                # Extract surrounding context
                start = max(0, page_lower.find(indicator) - 50)
                end = min(len(page_text), page_lower.find(indicator) + len(indicator) + 50)
                context = page_text[start:end]
                
                # Look for location pattern in context
                location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', context)
                if location_match:
                    potential_location = location_match.group(1).strip()
                    if is_valid_location(potential_location):
                        return potential_location
    
    # Strategy 4: Return safe default (prevents NOT NULL constraint error)
    return 'Location Not Available'


def is_valid_location(text: str) -> bool:
    """
    Check if extracted text looks like a valid location.
    Helps prevent false positives in location extraction.
    """
    if not text or len(text.strip()) < 2:
        return False
    
    text_clean = text.strip()
    
    # Skip if too long (likely not a location)
    if len(text_clean) > 100:
        return False
    
    # Skip obvious non-location text
    invalid_indicators = [
        'apply', 'job', 'save', 'share', 'view', 'click', 'button', 'link',
        'full-time', 'part-time', 'contract', 'salary', 'benefits', 'description',
        'requirements', 'qualifications', 'experience', 'skills', 'years',
        'degree', 'education', 'certification', 'training', 'software',
        'developer', 'engineer', 'manager', 'analyst', 'specialist',
        'follow', 'connect', 'message', 'post', 'profile', 'company'
    ]
    
    text_lower = text_clean.lower()
    if any(indicator in text_lower for indicator in invalid_indicators):
        return False
    
    # Check for valid location patterns
    valid_patterns = [
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Proper case city names
        r'[A-Z][a-z]+,\s*[A-Z]',  # City, State format
        r'(?i)(remote|hybrid|work from home)',  # Work arrangements
    ]
    
    for pattern in valid_patterns:
        if re.match(pattern, text_clean):
            return True
    
    # Additional validation for Australian locations
    australian_indicators = [
        'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
        'queensland', 'nsw', 'vic', 'wa', 'sa', 'tas', 'nt', 'act',
        'city', 'suburb', 'metro', 'cbd'
    ]
    
    if any(indicator in text_lower for indicator in australian_indicators):
        return True
    
    # If it passes basic checks and isn't obviously invalid, accept it
    return len(text_clean) >= 3 and len(text_clean) <= 50


def get_safe_job_data_for_save(job_data: Dict[str, Any], job_url: str, method_used: str) -> Dict[str, Any]:
    """
    Prepare job data for safe database save, ensuring all NOT NULL constraints are satisfied.
    This is the main function to use before saving JobPosting objects.
    """
    
    # Add method information to raw data
    job_data['scraping_method'] = method_used
    job_data['extraction_method'] = method_used.split('_')[0] if '_' in method_used else method_used
    
    # Clean and validate all data
    cleaned_data = clean_job_data(job_data, job_url)
    
    # Add URL
    cleaned_data['url'] = job_url
    
    # Final safety check - ensure no None values
    for key, value in cleaned_data.items():
        if value is None:
            if key in ['title', 'company', 'location']:
                cleaned_data[key] = f'{key.replace("_", " ").title()} Not Available'
            elif isinstance(value, bool):
                cleaned_data[key] = False
            else:
                cleaned_data[key] = ''
    
    return cleaned_data
