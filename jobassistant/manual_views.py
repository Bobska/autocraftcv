"""
Views for manual job entry and AI-powered content parsing
Enhanced with LinkedIn Login + Manual Entry capabilities
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
from .forms import ManualJobEntryForm, SmartManualEntryForm, LinkedInCredentialsForm
from .services.ai_content_parser import AIJobContentParser
from .services.anti_detection_scraper import SEEKSpecificScraper
from .services.linkedin_session_scraper import LinkedInSessionScraper
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


# Enhanced Manual Entry Views - LinkedIn Login + Manual Entry Enhancement

@require_http_methods(["GET", "POST"])
def enhanced_manual_job_entry(request):
    """Enhanced manual job entry with multiple options"""
    
    failed_url = request.GET.get('url', '')
    failed_reason = request.GET.get('reason', 'Automatic scraping failed')
    
    if request.method == 'GET':
        form = ManualJobEntryForm()
        
        context = {
            'form': form,
            'failed_url': failed_url,
            'failed_reason': failed_reason,
            'is_linkedin': 'linkedin.com' in failed_url.lower(),
            'page_title': 'Manual Job Entry Options'
        }
        
        return render(request, 'jobassistant/enhanced_manual_entry.html', context)
    
    elif request.method == 'POST':
        return handle_structured_manual_entry(request)


def handle_structured_manual_entry(request):
    """Handle structured manual job entry form submission"""
    
    try:
        form = ManualJobEntryForm(request.POST)
        failed_url = request.POST.get('failed_url', '')
        
        if form.is_valid():
            # Prepare data for safe saving
            job_data = {
                'url': failed_url or 'manual_entry',
                'title': form.cleaned_data['title'],
                'company': form.cleaned_data['company'],
                'location': form.cleaned_data['location'],
                'description': form.cleaned_data['description'],
                'requirements': form.cleaned_data['requirements'],
                'salary_range': form.cleaned_data['salary_range'],
                'employment_type': form.cleaned_data['employment_type'],
                'application_instructions': form.cleaned_data['application_instructions'],
                'extraction_method': 'manual_structured_entry',
                'raw_content': '',
                'needs_review': False
            }
            
            # Get safe data for saving
            safe_data = get_safe_job_data_for_save(job_data, failed_url or 'manual_entry', 'manual_structured_entry')
            
            # Save to database with safe data
            job = JobPosting.objects.create(**safe_data)
            
            logger.info(f"Successfully created job posting via manual entry: {job.title} (ID: {job.id})")
            
            # Store in session for progress tracking compatibility
            request.session['current_job_id'] = str(job.id)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'job_id': str(job.id),
                    'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
                    'method_used': 'manual_structured_entry',
                    'message': f'Successfully saved job posting: {job.title}'
                })
            
            messages.success(request, f'Successfully saved job posting: {job.title}')
            return redirect('jobassistant:job_details', job_id=job.id)
        
        else:
            # Form validation failed
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'Please correct the form errors and try again.'
                })
            
            messages.error(request, 'Please correct the form errors and try again.')
            return render(request, 'jobassistant/enhanced_manual_entry.html', {
                'form': form,
                'failed_url': request.POST.get('failed_url', ''),
                'errors': errors
            })
        
    except Exception as e:
        error_msg = f"Error saving manual job entry: {str(e)}"
        logger.error(error_msg)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
        return render(request, 'jobassistant/enhanced_manual_entry.html', {'errors': [error_msg]})


@require_http_methods(["GET", "POST"])
def smart_manual_entry(request):
    """Smart manual entry with AI-assisted parsing"""
    
    failed_url = request.GET.get('url', '')
    
    if request.method == 'GET':
        form = SmartManualEntryForm(initial={'job_url': failed_url})
        
        context = {
            'form': form,
            'failed_url': failed_url,
            'page_title': 'Smart Manual Entry'
        }
        
        return render(request, 'jobassistant/smart_manual_entry.html', context)
    
    elif request.method == 'POST':
        return handle_smart_manual_submission(request)


def handle_smart_manual_submission(request):
    """Handle AI-assisted manual job entry"""
    
    try:
        form = SmartManualEntryForm(request.POST)
        
        if form.is_valid():
            job_url = form.cleaned_data['job_url'] or request.GET.get('url', 'manual_entry')
            raw_content = form.cleaned_data['raw_content']
            
            logger.info(f"Processing smart manual entry for URL: {job_url}")
            logger.info(f"Content length: {len(raw_content)} characters")
            
            # Parse content with AI
            parser = AIJobContentParser()
            parsed_job = parser.parse_job_content(raw_content, job_url)
            
            # Prepare data for safe saving
            job_data = {
                'url': job_url,
                'title': parsed_job.get('title', 'AI Parsed Title'),
                'company': parsed_job.get('company', 'AI Parsed Company'),
                'location': parsed_job.get('location', 'AI Parsed Location'),
                'description': parsed_job.get('description', raw_content[:2000]),
                'requirements': parsed_job.get('requirements', 'Requirements Not Specified'),
                'responsibilities': parsed_job.get('responsibilities', ''),
                'salary_range': parsed_job.get('salary_range', ''),
                'employment_type': parsed_job.get('employment_type', ''),
                'application_instructions': parsed_job.get('application_instructions', ''),
                'extraction_method': 'smart_manual_ai_parsing',
                'raw_content': raw_content,
                'needs_review': parsed_job.get('needs_review', False)
            }
            
            # Get safe data for saving
            safe_data = get_safe_job_data_for_save(job_data, job_url, 'smart_manual_ai_parsing')
            
            # Save to database with safe data
            job = JobPosting.objects.create(**safe_data)
            
            logger.info(f"Successfully created job posting via smart manual entry: {job.title} (ID: {job.id})")
            logger.info(f"AI parsing quality: {parsed_job.get('extraction_quality', 'unknown')}")
            
            # Store in session for progress tracking compatibility
            request.session['current_job_id'] = str(job.id)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'job_id': str(job.id),
                    'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
                    'parsing_quality': parsed_job.get('extraction_quality', 'unknown'),
                    'ai_parsed': parsed_job.get('ai_parsed', False),
                    'needs_review': parsed_job.get('needs_review', False),
                    'method_used': 'smart_manual_ai_parsing'
                })
            
            messages.success(request, f'Successfully parsed and saved job posting: {job.title}')
            return redirect('jobassistant:job_details', job_id=job.id)
        
        else:
            # Form validation failed
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'Please correct the form errors and try again.'
                })
            
            messages.error(request, 'Please correct the form errors and try again.')
            return render(request, 'jobassistant/smart_manual_entry.html', {
                'form': form,
                'errors': errors
            })
        
    except Exception as e:
        error_msg = f"Error in smart manual job submission: {str(e)}"
        logger.error(error_msg)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
        return render(request, 'jobassistant/smart_manual_entry.html', {'errors': [error_msg]})


@require_http_methods(["GET", "POST"])
def linkedin_login_setup(request):
    """LinkedIn login setup for authenticated scraping"""
    
    job_url = request.GET.get('url', '')
    
    if request.method == 'GET':
        form = LinkedInCredentialsForm()
        
        context = {
            'form': form,
            'job_url': job_url,
            'page_title': 'LinkedIn Login Setup'
        }
        
        return render(request, 'jobassistant/linkedin_login_setup.html', context)
    
    elif request.method == 'POST':
        return handle_linkedin_login(request)


def handle_linkedin_login(request):
    """Handle LinkedIn login and authenticated scraping"""
    
    try:
        form = LinkedInCredentialsForm(request.POST)
        job_url = request.POST.get('job_url', '')
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            save_credentials = form.cleaned_data['save_credentials']
            
            logger.info(f"Attempting LinkedIn login for authenticated scraping: {job_url}")
            
            # Store credentials in session if requested
            if save_credentials:
                request.session['linkedin_email'] = email
                request.session['linkedin_password'] = password
                request.session['linkedin_credentials_saved'] = True
            
            # Create LinkedIn session scraper
            scraper = LinkedInSessionScraper(email=email, password=password)
            
            # Attempt authenticated scraping
            job_data = scraper.scrape_job_authenticated(job_url)
            
            if job_data and is_successful_extraction(job_data):
                # Prepare data for safe saving
                job_data['url'] = job_url
                job_data['extraction_method'] = 'linkedin_authenticated'
                
                # Get safe data for saving
                safe_data = get_safe_job_data_for_save(job_data, job_url, 'linkedin_authenticated')
                
                # Save to database with safe data
                job = JobPosting.objects.create(**safe_data)
                
                logger.info(f"Successfully created job posting via LinkedIn authentication: {job.title} (ID: {job.id})")
                
                # Store in session for progress tracking compatibility
                request.session['current_job_id'] = str(job.id)
                
                # Cleanup scraper
                scraper.cleanup()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'job_id': str(job.id),
                        'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
                        'method_used': 'linkedin_authenticated',
                        'message': f'Successfully scraped job via LinkedIn authentication: {job.title}'
                    })
                
                messages.success(request, f'Successfully scraped job via LinkedIn authentication: {job.title}')
                return redirect('jobassistant:job_details', job_id=job.id)
            
            else:
                # LinkedIn authentication failed or extraction was unsuccessful
                scraper.cleanup()
                
                error_msg = "LinkedIn authentication or extraction failed. Please try manual entry options."
                logger.warning(f"LinkedIn authenticated scraping failed for: {job_url}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'requires_manual_entry': True,
                        'manual_entry_options': {
                            'manual_form': reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}',
                            'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}'
                        },
                        'message': error_msg
                    })
                
                messages.warning(request, error_msg)
                return redirect(reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}&reason=linkedin_auth_failed')
        
        else:
            # Form validation failed
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'Please correct the form errors and try again.'
                })
            
            messages.error(request, 'Please correct the form errors and try again.')
            return render(request, 'jobassistant/linkedin_login_setup.html', {
                'form': form,
                'job_url': job_url,
                'errors': errors
            })
        
    except Exception as e:
        error_msg = f"Error in LinkedIn login process: {str(e)}"
        logger.error(error_msg)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
        return render(request, 'jobassistant/linkedin_login_setup.html', {'errors': [error_msg]})


@csrf_exempt
@require_http_methods(["POST"])
def enhanced_scraping_workflow(request):
    """Enhanced scraping workflow with LinkedIn login and manual fallbacks"""
    
    try:
        # Get request data
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        job_url = data.get('job_url', '').strip()
        scraping_method = data.get('scraping_method', 'auto')
        use_linkedin_login = data.get('use_linkedin_login', False)
        
        if not job_url:
            return JsonResponse({
                'success': False,
                'error': 'Job URL is required'
            }, status=400)
        
        logger.info(f"Starting enhanced scraping workflow for: {job_url} (method: {scraping_method})")
        
        # Step 1: Check if manual entry is explicitly requested
        if scraping_method == 'manual':
            return JsonResponse({
                'success': False,
                'requires_manual_entry': True,
                'manual_entry_options': {
                    'manual_form': reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}',
                    'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}'
                },
                'message': 'Manual entry requested.'
            })
        
        elif scraping_method == 'smart_manual':
            return JsonResponse({
                'success': False,
                'requires_manual_entry': True,
                'manual_entry_options': {
                    'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}'
                },
                'message': 'Smart manual entry requested.'
            })
        
        # Step 2: Try automatic scraping based on URL and options
        job_data = None
        method_used = 'unknown'
        
        if 'linkedin.com' in job_url.lower() and (use_linkedin_login or scraping_method == 'linkedin_auth'):
            # Try LinkedIn authenticated scraping
            if request.session.get('linkedin_credentials_saved'):
                email = request.session.get('linkedin_email')
                password = request.session.get('linkedin_password')
                
                if email and password:
                    scraper = LinkedInSessionScraper(email=email, password=password)
                    job_data = scraper.scrape_job_authenticated(job_url)
                    method_used = 'linkedin_authenticated'
                    scraper.cleanup()
            
            if not job_data:
                # LinkedIn auth required
                return JsonResponse({
                    'success': False,
                    'authentication_required': True,
                    'linkedin_login_url': reverse('jobassistant:linkedin_login_setup') + f'?url={job_url}',
                    'manual_entry_options': {
                        'manual_form': reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}',
                        'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}'
                    },
                    'message': 'LinkedIn authentication required for better results.'
                })
        
        elif 'seek.com' in job_url.lower():
            # Try SEEK specific scraping
            scraper = SEEKSpecificScraper()
            job_data, method_used = scraper.scrape_seek_job(job_url)
        
        else:
            # Try general anti-detection scraping
            from .services.anti_detection_scraper import AntiDetectionScraper
            scraper = AntiDetectionScraper()
            job_data, method_used = scraper.scrape_protected_site(job_url)
        
        # Step 3: Check if scraping was successful
        if job_data and is_successful_extraction(job_data):
            # Prepare data for safe saving
            job_data['url'] = job_url
            job_data['extraction_method'] = method_used
            
            # Get safe data for saving
            safe_data = get_safe_job_data_for_save(job_data, job_url, method_used)
            
            # Save to database with safe data
            job = JobPosting.objects.create(**safe_data)
            
            logger.info(f"Successfully created job posting via enhanced workflow: {job.title} (ID: {job.id})")
            
            # Store in session for progress tracking compatibility
            request.session['current_job_id'] = str(job.id)
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.id),
                'redirect_url': reverse('jobassistant:job_details', kwargs={'job_id': job.id}),
                'method_used': method_used,
                'extraction_quality': job_data.get('extraction_quality', 'good')
            })
        
        # Step 4: If scraping failed, offer manual options
        is_linkedin = 'linkedin.com' in job_url.lower()
        
        return JsonResponse({
            'success': False,
            'requires_manual_entry': True,
            'authentication_required': is_linkedin,
            'manual_entry_options': {
                'manual_form': reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}&reason=extraction_failed',
                'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}&reason=extraction_failed',
                'linkedin_login': reverse('jobassistant:linkedin_login_setup') + f'?url={job_url}' if is_linkedin else None
            },
            'method_used': method_used,
            'message': 'Automatic scraping failed. Please choose a manual entry option.'
        })
        
    except Exception as e:
        error_msg = f"Enhanced scraping workflow failed: {str(e)}"
        logger.error(error_msg)
        
        return JsonResponse({
            'success': False,
            'error': error_msg,
            'requires_manual_entry': True,
            'manual_entry_options': {
                'manual_form': reverse('jobassistant:enhanced_manual_entry') + f'?url={job_url}&reason=scraping_error',
                'smart_entry': reverse('jobassistant:smart_manual_entry') + f'?url={job_url}&reason=scraping_error'
            }
        }, status=500)
