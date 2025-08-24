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
