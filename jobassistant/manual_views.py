"""
Views for manual job entry and AI-powered content parsing
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
import json
import logging
from urllib.parse import unquote

from .models import JobPosting
from .services.ai_content_parser import AIJobContentParser
from .services.anti_detection_scraper import SEEKSpecificScraper
from .safe_data_utils import get_safe_job_data_for_save, clean_job_data

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def manual_job_entry(request):
    """Manual job entry view when automatic scraping fails"""
    
    if request.method == 'GET':
        # Get the failed URL from query parameters
        failed_url = request.GET.get('url', '')
        failed_reason = request.GET.get('reason', 'Automatic scraping failed')
        
        context = {
            'failed_url': failed_url,
            'failed_reason': failed_reason,
            'page_title': 'Manual Job Entry Required'
        }
        
        return render(request, 'jobassistant/manual_job_entry.html', context)
    
    elif request.method == 'POST':
        return handle_manual_job_submission(request)


def handle_manual_job_submission(request):
    """Handle manual job content submission and AI parsing"""
    
    try:
        # Get form data
        job_url = request.POST.get('job_url', '').strip()
        job_content = request.POST.get('job_content', '').strip()
        
        # Validate input
        if not job_content:
            return JsonResponse({
                'success': False,
                'error': 'Job content is required. Please paste the job posting content.'
            }, status=400)
        
        if len(job_content) < 100:
            return JsonResponse({
                'success': False,
                'error': 'Job content too short. Please paste the complete job posting.'
            }, status=400)
        
        logger.info(f"Processing manual job entry for URL: {job_url}")
        logger.info(f"Content length: {len(job_content)} characters")
        
        # Parse content with AI
        parser = AIJobContentParser()
        parsed_job = parser.parse_job_content(job_content, job_url)
        
        # Prepare data for safe saving
        job_data = {
            'url': job_url or 'manual_entry',
            'title': parsed_job.get('title', 'AI Parsed Title'),
            'company': parsed_job.get('company', 'AI Parsed Company'), 
            'location': parsed_job.get('location', 'AI Parsed Location'),
            'description': parsed_job.get('description', job_content[:2000]),
            'requirements': parsed_job.get('requirements', 'Requirements Not Specified'),
            'responsibilities': parsed_job.get('responsibilities', ''),
            'salary_range': parsed_job.get('salary_range', ''),
            'employment_type': parsed_job.get('employment_type', ''),
            'extraction_method': 'manual_ai_parsing',
            'raw_content': job_content,
            'needs_review': parsed_job.get('needs_review', False)
        }
        
        # Get safe data for saving
        safe_data = get_safe_job_data_for_save(job_data, job_url or 'manual_entry', 'manual_ai_parsing')
        
        # Save to database with safe data
        job = JobPosting.objects.create(**safe_data)
        
        logger.info(f"Successfully created job posting with ID: {job.id}")
        logger.info(f"AI parsing quality: {parsed_job.get('extraction_quality', 'unknown')}")
        
        # Store in session for progress tracking compatibility
        request.session['current_job_id'] = str(job.id)
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
            'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
            'parsing_quality': parsed_job.get('extraction_quality', 'unknown'),
            'ai_parsed': parsed_job.get('ai_parsed', False),
            'needs_review': parsed_job.get('needs_review', False)
        })
        
    except Exception as e:
        logger.error(f"Error in manual job submission: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to process job content: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def enhanced_scrape_job(request):
    """Enhanced job scraping with anti-detection and manual fallback"""
    
    try:
        # Get job URL
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        job_url = data.get('job_url', '').strip()
        
        if not job_url:
            return JsonResponse({
                'success': False,
                'error': 'Job URL is required'
            }, status=400)
        
        logger.info(f"Starting enhanced scraping for: {job_url}")
        
        # Determine scraping strategy based on URL
        if 'seek.com' in job_url.lower():
            scraper = SEEKSpecificScraper()
            job_data, method = scraper.scrape_seek_job(job_url)
        else:
            # Use general anti-detection scraper for other sites
            from .services.anti_detection_scraper import AntiDetectionScraper
            scraper = AntiDetectionScraper()
            job_data, method = scraper.scrape_protected_site(job_url)
        
        # Check if manual entry is required
        if job_data.get('manual_entry_required') or job_data.get('requires_manual_fallback'):
            return JsonResponse({
                'success': False,
                'requires_manual_entry': True,
                'manual_entry_url': reverse('jobassistant:manual_job_entry') + f'?url={job_url}&reason=anti_bot_protection',
                'message': 'Automatic scraping failed due to anti-bot protection. Manual entry required.',
                'method_used': method,
                'anti_bot_detected': job_data.get('anti_bot_detected', False)
            })
        
        # Check if extraction was successful
        if not is_successful_extraction(job_data):
            return JsonResponse({
                'success': False,
                'requires_manual_entry': True,
                'manual_entry_url': reverse('jobassistant:manual_job_entry') + f'?url={job_url}&reason=extraction_failed',
                'message': 'Automatic extraction failed to get meaningful job data. Manual entry recommended.',
                'method_used': method,
                'extracted_data': job_data
            })
        
        # Save successful extraction
        job_data_dict = {
            'url': job_url,
            'title': job_data.get('title', 'Title Not Available'),
            'company': job_data.get('company', 'Company Not Available'),
            'location': job_data.get('location', 'Location Not Available'),
            'description': job_data.get('description', 'Description Not Available'),
            'requirements': job_data.get('requirements', ''),
            'responsibilities': job_data.get('responsibilities', ''),
            'salary_range': job_data.get('salary_range', ''),
            'employment_type': job_data.get('employment_type', ''),
            'extraction_method': method,
            'raw_content': job_data.get('raw_content', '')[:10000],
            'site_domain': job_data.get('site_domain', ''),
            'needs_review': False
        }
        
        # Get safe data for saving
        safe_data = get_safe_job_data_for_save(job_data_dict, job_url, method)
        
        # Create job posting with safe data
        job = JobPosting.objects.create(**safe_data)
        
        logger.info(f"Successfully scraped and saved job with ID: {job.id}")
        
        # Store in session
        request.session['current_job_id'] = str(job.id)
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
            'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
            'method_used': method,
            'site_domain': job_data.get('site_domain', ''),
            'extraction_quality': 'good'
        })
        
    except Exception as e:
        logger.error(f"Enhanced scraping failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'requires_manual_entry': True,
            'manual_entry_url': reverse('jobassistant:manual_job_entry') + f'?url={job_url}&reason=scraping_error'
        }, status=500)


def is_successful_extraction(job_data: dict) -> bool:
    """Check if job data extraction was successful"""
    
    if not job_data:
        return False
    
    # Check for meaningful title
    title = job_data.get('title', '')
    has_title = (title and 
                len(title) > 5 and 
                'extraction failed' not in title.lower() and
                'manual entry required' not in title.lower() and
                'manual review required' not in title.lower())
    
    # Check for meaningful company
    company = job_data.get('company', '')
    has_company = (company and 
                  len(company) > 2 and 
                  'extraction failed' not in company.lower() and
                  'manual entry required' not in company.lower() and
                  'manual review required' not in company.lower())
    
    # Check for meaningful description
    description = job_data.get('description', '')
    has_description = (description and 
                      len(description) > 100 and 
                      'extraction failed' not in description.lower() and
                      'manual entry required' not in description.lower())
    
    # Must have at least title + company OR title + description
    return (has_title and has_company) or (has_title and has_description)


@require_http_methods(["GET"])
def manual_entry_help(request):
    """Help page for manual job entry process"""
    
    context = {
        'page_title': 'Manual Job Entry Help',
    }
    
    return render(request, 'jobassistant/manual_entry_help.html', context)


@require_http_methods(["POST"])
def retry_scraping(request):
    """Retry scraping with different strategy"""
    
    try:
        job_url = request.POST.get('job_url', '').strip()
        
        if not job_url:
            return JsonResponse({
                'success': False,
                'error': 'Job URL is required'
            }, status=400)
        
        # Try with enhanced anti-detection scraper
        from .services.anti_detection_scraper import AntiDetectionScraper
        scraper = AntiDetectionScraper()
        job_data, method = scraper.scrape_protected_site(job_url)
        
        if is_successful_extraction(job_data):
            return JsonResponse({
                'success': True,
                'job_data': job_data,
                'method_used': method,
                'message': 'Retry successful!'
            })
        else:
            return JsonResponse({
                'success': False,
                'requires_manual_entry': True,
                'message': 'Retry failed. Manual entry recommended.',
                'method_used': method
            })
        
    except Exception as e:
        logger.error(f"Retry scraping failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
