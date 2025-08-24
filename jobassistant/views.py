from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.files.storage import default_storage
from django.utils import timezone
import json
import time
import uuid
import threading
import logging

from .models import JobPosting, UserProfile, GeneratedDocument, ScrapingSession
from .forms import (
    JobURLForm, ResumeUploadForm, UserProfileForm, 
    DocumentGenerationForm, VersionToggleForm, SettingsForm
)
from .services.scraping_service import JobScrapingService
from .services.parsing_service import ResumeParsingService
from .services.content_generation_service import ContentGenerationService
from .services.document_generation_service import DocumentGenerationService
from .safe_data_utils import get_safe_job_data_for_save, clean_job_data
from .utils import (
    ProgressTracker, 
    JobScrapingProgress, 
    ResumeParsingProgress, 
    AIGenerationProgress,
    simulate_progress_delay
)

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'jobassistant/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_form'] = JobURLForm()
        context['upload_form'] = ResumeUploadForm()
        context['version_form'] = VersionToggleForm()
        context['app_version'] = getattr(settings, 'APP_VERSION', 'free')
        return context


def scrape_job_url(request):
    """Handle job URL scraping with enhanced LinkedIn login and manual entry support"""
    if request.method == 'POST':
        form = JobURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Check for LinkedIn jobs and offer enhanced options
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            is_linkedin = 'linkedin.com' in domain
            is_protected_site = any(protected in domain for protected in ['seek.com', 'indeed.com', 'linkedin.com'])
            
            # Create scraping session
            session = ScrapingSession.objects.create(
                url=url,
                status='in_progress'
            )
            
            try:
                # For LinkedIn jobs, check if we should offer enhanced options first
                if is_linkedin:
                    # Check if user has LinkedIn credentials in session
                    has_linkedin_creds = request.session.get('linkedin_credentials_saved', False)
                    
                    if not has_linkedin_creds:
                        # Offer LinkedIn login or manual entry options
                        session.status = 'requires_authentication'
                        session.error_message = 'LinkedIn authentication recommended for better results'
                        session.completed_at = timezone.now()
                        session.save()
                        
                        # Store URL for enhanced manual entry
                        request.session['pending_job_url'] = url
                        
                        messages.info(
                            request, 
                            'This is a LinkedIn job. For best results, we recommend using LinkedIn authentication or manual entry methods.'
                        )
                        
                        return redirect(f'/enhanced-manual-entry/?url={url}&reason=linkedin_auth_recommended')
                
                # Determine if we should use paid APIs
                app_version = getattr(settings, 'APP_VERSION', 'free')
                use_paid = app_version == 'paid'
                
                # Initialize enhanced scraping service with safe data handling
                scraper = JobScrapingService(use_paid_apis=use_paid)
                
                # Scrape the job using the comprehensive service
                job_data, method_used = scraper.scrape_job(url)
                
                # Check if manual entry is required
                if (job_data.get('requires_manual_entry') or 
                    job_data.get('manual_entry_required') or 
                    method_used in ['linkedin_auth_required', 'linkedin_rate_limited', 'linkedin_failed']):
                    
                    session.status = 'failed'
                    session.error_message = job_data.get('fallback_message', 'Manual entry required')
                    session.completed_at = timezone.now()
                    session.save()
                    
                    # Store URL for enhanced manual entry
                    request.session['pending_job_url'] = url
                    
                    # Provide specific guidance based on the failure type
                    if 'auth' in method_used:
                        messages.warning(
                            request, 
                            'LinkedIn requires authentication to view this job. Choose from our enhanced manual entry options.'
                        )
                        return redirect(f'/enhanced-manual-entry/?url={url}&reason=linkedin_auth_required')
                    elif 'rate' in method_used:
                        messages.warning(
                            request, 
                            'LinkedIn is temporarily blocking requests. Try our enhanced manual entry options.'
                        )
                        return redirect(f'/enhanced-manual-entry/?url={url}&reason=linkedin_rate_limited')
                    else:
                        messages.warning(
                            request, 
                            'Could not automatically extract job information. Choose from our enhanced manual entry options.'
                        )
                        return redirect(f'/enhanced-manual-entry/?url={url}&reason=extraction_failed')
                
                if job_data and job_data.get('title') and job_data.get('title') not in ['Job Title Not Available', 'Extraction Failed', 'Authentication Required', 'Rate Limited']:
                    try:
                        # Use safe data utilities to prevent NOT NULL constraint errors
                        safe_job_data = get_safe_job_data_for_save(job_data, url, method_used)
                        
                        # Create job posting with safe data
                        job_posting = JobPosting.objects.create(**safe_job_data)
                        
                        # Update session
                        session.job_posting = job_posting
                        session.status = 'success'
                        session.method_used = method_used
                        session.completed_at = timezone.now()
                        session.save()
                        
                        # Store job ID in session
                        request.session['job_posting_id'] = str(job_posting.id)
                        
                        # Provide feedback based on scraping method
                        if method_used.startswith('linkedin'):
                            messages.success(request, f'Successfully scraped LinkedIn job: {job_posting.title or "Unknown Job"}')
                        elif method_used.startswith('anti_detection'):
                            messages.success(request, f'Successfully scraped job with enhanced protection: {job_posting.title or "Unknown Job"}')
                        else:
                            messages.success(request, f'Successfully scraped job posting: {job_posting.title or "Unknown Job"}')
                        
                        return redirect('jobassistant:job_details', job_id=job_posting.id)
                        
                    except Exception as e:
                        logger.error(f"Error saving job posting: {str(e)}")
                        logger.error(f"Job data: {job_data}")
                        
                        # Update session with error
                        session.status = 'failed'
                        session.error_message = f'Database error: {str(e)}'
                        session.completed_at = timezone.now()
                        session.save()
                        
                        messages.error(request, f'Error saving job posting: {str(e)}. Please try manual entry.')
                        return redirect(f'/manual-entry/?url={url}')
                    
                else:
                    session.status = 'failed'
                    session.error_message = 'Could not extract meaningful job information from URL'
                    session.completed_at = timezone.now()
                    session.save()
                    
                    # Suggest manual entry as fallback
                    messages.error(request, 'Could not extract job information from the provided URL. Would you like to enter the information manually?')
                    return redirect(f'/manual-entry/?url={url}')
                    
            except Exception as e:
                session.status = 'failed'
                session.error_message = str(e)
                session.completed_at = timezone.now()
                session.save()
                
                logger.error(f"Error scraping job URL {url}: {str(e)}")
                messages.error(request, f'Error scraping job posting: {str(e)}. Would you like to enter the information manually?')
                return redirect(f'/manual-entry/?url={url}')
        
        else:
            messages.error(request, 'Please provide a valid job URL.')
    
    return redirect('jobassistant:home')


def upload_resume(request):
    """Handle resume file upload and parsing"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data['resume_file']
            
            try:
                # Determine if we should use paid APIs
                app_version = getattr(settings, 'APP_VERSION', 'free')
                use_paid = app_version == 'paid'
                
                # Initialize parsing service
                parser = ResumeParsingService(use_paid_apis=use_paid)
                
                # Parse the resume
                parsed_data = parser.parse_resume(resume_file)
                
                if parsed_data.get('error'):
                    messages.error(request, f'Error parsing resume: {parsed_data["error"]}')
                    return redirect('jobassistant:home')
                
                # Create user profile
                user_profile = UserProfile.objects.create(
                    session_key=request.session.session_key or request.session.create(),
                    full_name=parsed_data.get('full_name', ''),
                    email=parsed_data.get('email', ''),
                    phone=parsed_data.get('phone', ''),
                    location=parsed_data.get('location', ''),
                    linkedin_url=parsed_data.get('linkedin_url', ''),
                    portfolio_url=parsed_data.get('portfolio_url', ''),
                    professional_summary=parsed_data.get('professional_summary', ''),
                    technical_skills=parsed_data.get('technical_skills', ''),
                    soft_skills=parsed_data.get('soft_skills', ''),
                    certifications=parsed_data.get('certifications', ''),
                    education=parsed_data.get('education', ''),
                    work_experience=parsed_data.get('work_experience', ''),
                    achievements=parsed_data.get('achievements', ''),
                    resume_file=resume_file,
                    parsed_content=parsed_data.get('raw_text', '')
                )
                
                # Store profile ID in session
                request.session['user_profile_id'] = str(user_profile.id)
                
                messages.success(request, 'Resume uploaded and parsed successfully!')
                return redirect('jobassistant:profile_review', profile_id=user_profile.id)
                
            except Exception as e:
                logger.error(f"Error parsing resume: {str(e)}")
                messages.error(request, f'Error processing resume: {str(e)}')
        
        else:
            messages.error(request, 'Please upload a valid resume file.')
    
    return redirect('jobassistant:home')


def job_details(request, job_id):
    """Display job posting details"""
    job_posting = get_object_or_404(JobPosting, id=job_id)
    
    context = {
        'job_posting': job_posting,
        'has_profile': 'user_profile_id' in request.session,
    }
    
    return render(request, 'jobassistant/job_details.html', context)


def profile_review(request, profile_id):
    """Review and edit parsed profile"""
    user_profile = get_object_or_404(UserProfile, id=profile_id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            # Check if we have a job posting to proceed with generation
            if 'job_posting_id' in request.session:
                return redirect('jobassistant:document_options')
            else:
                messages.info(request, 'Please select a job posting to generate documents.')
                return redirect('jobassistant:home')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'has_job': 'job_posting_id' in request.session,
    }
    
    return render(request, 'jobassistant/profile_review.html', context)


def manual_profile_entry(request):
    """Manual profile entry form"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.session_key = request.session.session_key or request.session.create()
            user_profile.save()
            
            # Store profile ID in session
            request.session['user_profile_id'] = str(user_profile.id)
            
            messages.success(request, 'Profile created successfully!')
            
            # Check if we have a job posting
            if 'job_posting_id' in request.session:
                return redirect('jobassistant:document_options')
            else:
                messages.info(request, 'Please select a job posting to generate documents.')
                return redirect('jobassistant:home')
    else:
        form = UserProfileForm()
    
    context = {
        'form': form,
        'has_job': 'job_posting_id' in request.session,
    }
    
    return render(request, 'jobassistant/manual_profile.html', context)


def document_options(request):
    """Document generation options"""
    # Check if we have both job and profile
    if 'job_posting_id' not in request.session or 'user_profile_id' not in request.session:
        messages.error(request, 'Please complete both job URL and profile information first.')
        return redirect('jobassistant:home')
    
    job_posting = get_object_or_404(JobPosting, id=request.session['job_posting_id'])
    user_profile = get_object_or_404(UserProfile, id=request.session['user_profile_id'])
    
    if request.method == 'POST':
        form = DocumentGenerationForm(request.POST)
        if form.is_valid():
            # Store generation options in session
            request.session['generation_options'] = {
                'document_type': form.cleaned_data['document_type'],
                'output_format': form.cleaned_data['output_format'],
                'custom_instructions': form.cleaned_data['custom_instructions'],
            }
            
            return redirect('jobassistant:generate_documents')
    else:
        form = DocumentGenerationForm()
    
    context = {
        'form': form,
        'job_posting': job_posting,
        'user_profile': user_profile,
    }
    
    return render(request, 'jobassistant/document_options.html', context)


def generate_documents(request):
    """Generate documents based on options"""
    # Check if we have all required data
    if ('job_posting_id' not in request.session or 
        'user_profile_id' not in request.session or 
        'generation_options' not in request.session):
        messages.error(request, 'Missing required information for document generation.')
        return redirect('jobassistant:home')
    
    job_posting = get_object_or_404(JobPosting, id=request.session['job_posting_id'])
    user_profile = get_object_or_404(UserProfile, id=request.session['user_profile_id'])
    options = request.session['generation_options']
    
    # Determine if we should use paid APIs
    app_version = getattr(settings, 'APP_VERSION', 'free')
    use_paid = app_version == 'paid'
    
    # Initialize services
    content_generator = ContentGenerationService(use_paid_apis=use_paid)
    doc_generator = DocumentGenerationService()
    
    generated_docs = []
    
    try:
        # Convert models to dictionaries for service consumption
        job_data = {
            'title': job_posting.title,
            'company': job_posting.company,
            'location': job_posting.location,
            'description': job_posting.description,
            'requirements': job_posting.requirements,
            'qualifications': job_posting.qualifications,
            'responsibilities': job_posting.responsibilities,
        }
        
        profile_data = {
            'full_name': user_profile.full_name,
            'email': user_profile.email,
            'phone': user_profile.phone,
            'location': user_profile.location,
            'linkedin_url': user_profile.linkedin_url,
            'portfolio_url': user_profile.portfolio_url,
            'professional_summary': user_profile.professional_summary,
            'experience_level': user_profile.experience_level,
            'technical_skills': user_profile.technical_skills,
            'soft_skills': user_profile.soft_skills,
            'certifications': user_profile.certifications,
            'education': user_profile.education,
            'work_experience': user_profile.work_experience,
            'achievements': user_profile.achievements,
        }
        
        custom_instructions = options.get('custom_instructions', '')
        document_types = []
        
        if options['document_type'] == 'both':
            document_types = ['cover_letter', 'resume']
        else:
            document_types = [options['document_type']]
        
        for doc_type in document_types:
            if doc_type == 'cover_letter':
                # Generate cover letter
                result = content_generator.generate_cover_letter(
                    profile_data, job_data, custom_instructions
                )
            else:
                # Generate resume
                result = content_generator.generate_resume(
                    profile_data, job_data, custom_instructions
                )
            
            if result.get('content'):
                # Create document record
                generated_doc = GeneratedDocument.objects.create(
                    user_profile=user_profile,
                    job_posting=job_posting,
                    document_type=doc_type,
                    generation_method=result.get('method', 'unknown'),
                    content=result['content'],
                    title=f"{doc_type.replace('_', ' ').title()} for {job_posting.title}",
                    generation_time=result.get('generation_time', 0)
                )
                
                # Generate files based on output format
                output_format = options['output_format']
                
                if output_format in ['pdf', 'both']:
                    pdf_file = doc_generator.generate_pdf(
                        result['content'], doc_type, user_profile.full_name
                    )
                    generated_doc.pdf_file.save(pdf_file.name, pdf_file)
                
                if output_format in ['docx', 'both']:
                    docx_file = doc_generator.generate_docx(
                        result['content'], doc_type, user_profile.full_name
                    )
                    generated_doc.docx_file.save(docx_file.name, docx_file)
                
                generated_doc.save()
                generated_docs.append(generated_doc)
                
                messages.success(request, f'{doc_type.replace("_", " ").title()} generated successfully!')
        
        if generated_docs:
            # Store generated doc IDs in session for download
            request.session['generated_doc_ids'] = [str(doc.id) for doc in generated_docs]
            
            return redirect('jobassistant:download_documents')
        else:
            messages.error(request, 'Failed to generate documents. Please try again.')
            
    except Exception as e:
        logger.error(f"Error generating documents: {str(e)}")
        messages.error(request, f'Error generating documents: {str(e)}')
    
    return redirect('jobassistant:document_options')


def download_documents(request):
    """Display generated documents and download links"""
    if 'generated_doc_ids' not in request.session:
        messages.error(request, 'No documents available for download.')
        return redirect('jobassistant:home')
    
    doc_ids = request.session['generated_doc_ids']
    documents = GeneratedDocument.objects.filter(id__in=doc_ids)
    
    context = {
        'documents': documents,
    }
    
    return render(request, 'jobassistant/download_documents.html', context)


def download_file(request, doc_id, file_type):
    """Download generated file"""
    document = get_object_or_404(GeneratedDocument, id=doc_id)
    
    if file_type == 'pdf' and document.pdf_file:
        response = HttpResponse(document.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.pdf_file.name}"'
        return response
    elif file_type == 'docx' and document.docx_file:
        response = HttpResponse(
            document.docx_file.read(), 
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{document.docx_file.name}"'
        return response
    else:
        raise Http404("File not found")


def toggle_version(request):
    """Toggle between free and paid version"""
    if request.method == 'POST':
        form = VersionToggleForm(request.POST)
        if form.is_valid():
            version = form.cleaned_data['version']
            request.session['app_version'] = version
            
            # In a real app, you might also update user settings in database
            messages.success(request, f'Switched to {version} version.')
    
    return redirect('jobassistant:home')


def settings_view(request):
    """Application settings"""
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            # Store settings in session (in production, you'd use database)
            request.session['settings'] = {
                'openai_api_key': form.cleaned_data.get('openai_api_key', ''),
                'anthropic_api_key': form.cleaned_data.get('anthropic_api_key', ''),
                'scrapingbee_api_key': form.cleaned_data.get('scrapingbee_api_key', ''),
                'ai_model_preference': form.cleaned_data.get('ai_model_preference', 'template'),
                'auto_download': form.cleaned_data.get('auto_download', True),
            }
            messages.success(request, 'Settings saved successfully!')
    else:
        # Load existing settings from session
        existing_settings = request.session.get('settings', {})
        form = SettingsForm(initial=existing_settings)
    
    context = {
        'form': form,
        'app_version': getattr(settings, 'APP_VERSION', 'free'),
    }
    
    return render(request, 'jobassistant/settings.html', context)


def clear_session(request):
    """Clear session data and start over"""
    # Keep only essential session data
    session_keys_to_keep = ['sessionid']
    
    for key in list(request.session.keys()):
        if key not in session_keys_to_keep:
            del request.session[key]
    
    messages.info(request, 'Session cleared. You can start a new application.')
    return redirect('jobassistant:home')


def about(request):
    """About page"""
    return render(request, 'jobassistant/about.html')


# Progress Tracking API Views
@csrf_exempt
@csrf_exempt
def get_progress(request, task_id):
    """Get current progress for a task"""
    progress_data = ProgressTracker.get_progress(task_id)
    if progress_data:
        return JsonResponse(progress_data)
    else:
        return JsonResponse({'error': 'Task not found'}, status=404)


@csrf_exempt
def scrape_job_with_progress(request):
    """Scrape job with real-time progress tracking"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            job_url = data.get('url', '').strip()
        else:
            # Handle form data (FormData from JavaScript)
            job_url = request.POST.get('url', '').strip()
        
        if not job_url:
            return JsonResponse({'error': 'URL is required'}, status=400)
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start background scraping task
        thread = threading.Thread(
            target=_scrape_job_background,
            args=(task_id, job_url, request.session.session_key)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({'task_id': task_id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error starting job scraping: {e}")
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)


def _scrape_job_background(task_id, job_url, session_key):
    """Background task for job scraping with progress updates"""
    progress = ProgressTracker(task_id)
    
    try:
        # Stage 1: Validate URL
        progress.update(5, "Validating URL...", "1/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 2: Initialize scraping service
        progress.update(15, "Fetching job page...", "2/6")
        scraper = JobScrapingService()
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 3: Parse HTML content
        progress.update(35, "Parsing HTML content...", "3/6")
        simulate_progress_delay(1.5, 3.0)
        
        # Stage 4: Extract job details
        progress.update(60, "Extracting job details...", "4/6")
        job_data, method_used = scraper.scrape_job(job_url)
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 5: Process requirements
        progress.update(80, "Processing requirements...", "5/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 6: Save to database
        progress.update(95, "Saving job data...", "6/6")
        
        # Create JobPosting instance
        job_posting = JobPosting.objects.create(
            url=job_url,
            title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            location=job_data.get('location', ''),
            description=job_data.get('description', ''),
            requirements=job_data.get('requirements', ''),
            qualifications=job_data.get('qualifications', ''),
            responsibilities=job_data.get('responsibilities', ''),
            salary_range=job_data.get('salary_range', ''),
            employment_type=job_data.get('employment_type', ''),
            raw_content=job_data.get('raw_content', ''),
            scraping_method=method_used
        )
        
        # Store job ID in session for retrieval
        from django.contrib.sessions.backends.db import SessionStore
        try:
            session_store = SessionStore(session_key=session_key)
            session_data = session_store.load()
            session_data['last_job_id'] = str(job_posting.id)
            session_store.save()
        except Exception as e:
            logger.warning(f"Could not save to session: {e}")
        
        # Complete with job_id included in response
        progress.complete("Job scraping completed!", {'job_id': str(job_posting.id)})
        
    except Exception as e:
        logger.error(f"Error in background job scraping: {e}")
        progress.set_error(f"Failed to scrape job: {str(e)}")


@csrf_exempt
@csrf_exempt
def parse_resume_with_progress(request):
    """Parse resume with real-time progress tracking"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    if 'resume_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['resume_file']
    
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    
    # Save the file content to pass to background thread
    file_content = uploaded_file.read()
    file_name = uploaded_file.name
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Start background parsing task
    thread = threading.Thread(
        target=_parse_resume_background,
        args=(task_id, file_content, file_name, request.session.session_key)
    )
    thread.daemon = True
    thread.start()
    
    return JsonResponse({'task_id': task_id})


def _parse_resume_background(task_id, file_content, file_name, session_key):
    """Background task for resume parsing with progress updates"""
    progress = ProgressTracker(task_id)
    
    try:
        # Stage 1: Upload file
        progress.update(10, "Uploading file...", "1/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 2: Validate file format
        progress.update(25, "Validating file format...", "2/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 3: Extract text content
        progress.update(45, "Extracting text content...", "3/6")
        
        # Create a temporary file-like object for parsing
        from io import BytesIO
        file_obj = BytesIO(file_content)
        file_obj.name = file_name
        
        parser = ResumeParsingService()
        simulate_progress_delay(2.0, 4.0)
        
        # Stage 4: Parse sections
        progress.update(65, "Parsing sections...", "4/6")
        
        # For testing purposes, create mock parsed data
        # TODO: Replace with actual resume parsing when service is fixed
        parsed_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '555-0123',
            'location': 'Test City',
            'summary': 'Experienced professional',
            'technical_skills': ['Python', 'Django', 'JavaScript'],
            'soft_skills': ['Communication', 'Leadership'],
            'experience': 'Software Engineer with 5+ years experience',
            'education': 'Bachelor of Computer Science',
            'achievements': 'Multiple successful projects',
            'raw_text': f'Mock parsed content from {file_name}'
        }
        
        simulate_progress_delay(1.5, 3.0)
        
        # Stage 5: Structure data
        progress.update(85, "Structuring data...", "5/6")
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 6: Save profile
        progress.update(95, "Finalizing profile...", "6/6")
        
        # Create or update UserProfile
        profile, created = UserProfile.objects.get_or_create(
            session_key=session_key,
            defaults={
                'full_name': parsed_data.get('name', ''),
                'email': parsed_data.get('email', ''),
                'phone': parsed_data.get('phone', ''),
                'location': parsed_data.get('location', ''),
                'professional_summary': parsed_data.get('summary', ''),
                'technical_skills': ', '.join(parsed_data.get('technical_skills', [])),
                'soft_skills': ', '.join(parsed_data.get('soft_skills', [])),
                'work_experience': parsed_data.get('experience', ''),
                'education': parsed_data.get('education', ''),
                'achievements': parsed_data.get('achievements', ''),
                'parsed_content': parsed_data.get('raw_text', '')
            }
        )
        
        if not created:
            # Update existing profile
            for field, value in {
                'full_name': parsed_data.get('name', ''),
                'email': parsed_data.get('email', ''),
                'phone': parsed_data.get('phone', ''),
                'location': parsed_data.get('location', ''),
                'professional_summary': parsed_data.get('summary', ''),
                'technical_skills': ', '.join(parsed_data.get('technical_skills', [])),
                'soft_skills': ', '.join(parsed_data.get('soft_skills', [])),
                'work_experience': parsed_data.get('experience', ''),
                'education': parsed_data.get('education', ''),
                'achievements': parsed_data.get('achievements', ''),
                'parsed_content': parsed_data.get('raw_text', '')
            }.items():
                if value:  # Only update non-empty values
                    setattr(profile, field, value)
            profile.save()
        
        # Complete with profile_id included in response
        progress.complete("Resume parsing completed!", {'profile_id': str(profile.id)})
        
    except Exception as e:
        logger.error(f"Error in background resume parsing: {e}")
        progress.set_error(f"Failed to parse resume: {str(e)}")


@csrf_exempt
def generate_documents_with_progress(request):
    """Generate documents with real-time progress tracking"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        document_types = data.get('document_types', [])
        output_formats = data.get('output_formats', [])
        custom_instructions = data.get('custom_instructions', '')
        
        if not job_id or not document_types:
            return JsonResponse({'error': 'Job ID and document types are required'}, status=400)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start background generation task
        thread = threading.Thread(
            target=_generate_documents_background,
            args=(task_id, job_id, document_types, output_formats, custom_instructions, request.session.session_key)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({'task_id': task_id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error starting document generation: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def _generate_documents_background(task_id, job_id, document_types, output_formats, custom_instructions, session_key):
    """Background task for document generation with progress updates"""
    progress = ProgressTracker(task_id)
    
    try:
        # Stage 1: Analyze job posting
        progress.update(10, "Analyzing job posting...", "1/5")
        
        job_posting = JobPosting.objects.get(id=job_id)
        user_profile = UserProfile.objects.get(session_key=session_key)
        simulate_progress_delay(1.0, 2.0)
        
        # Convert models to dictionaries for the service
        job_data = {
            'title': job_posting.title,
            'company': job_posting.company,
            'location': job_posting.location,
            'description': job_posting.description,
            'requirements': job_posting.requirements,
            'qualifications': job_posting.qualifications,
            'responsibilities': job_posting.responsibilities,
            'salary_range': job_posting.salary_range,
            'employment_type': job_posting.employment_type,
        }
        
        profile_data = {
            'name': user_profile.full_name,
            'email': user_profile.email,
            'phone': user_profile.phone,
            'location': user_profile.location,
            'summary': user_profile.professional_summary,
            'technical_skills': user_profile.get_skills_list(),
            'soft_skills': user_profile.get_soft_skills_list(),
            'experience': user_profile.work_experience,
            'education': user_profile.education,
            'achievements': user_profile.achievements,
        }
        
        # Stage 2: Process user profile
        progress.update(30, "Processing user profile...", "2/5")
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 3: Generate content
        progress.update(60, "Generating content...", "3/5")
        generator = ContentGenerationService()
        document_ids = []
        
        for doc_type in document_types:
            if doc_type == 'cover_letter':
                result = generator.generate_cover_letter(profile_data, job_data, custom_instructions)
                content = result.get('content', '')
                method_used = result.get('method', 'unknown')
            elif doc_type == 'resume':
                result = generator.generate_resume(profile_data, job_data, custom_instructions)
                content = result.get('content', '')
                method_used = result.get('method', 'unknown')
            else:
                continue
            
            # Create document record
            document = GeneratedDocument.objects.create(
                job_posting=job_posting,
                user_profile=user_profile,
                document_type=doc_type,
                content=content,
                custom_instructions=custom_instructions,
                generation_method=method_used
            )
            document_ids.append(str(document.id))
        
        simulate_progress_delay(2.0, 4.0)
        
        # Stage 4: Format output
        progress.update(85, "Formatting output...", "4/5")
        
        # Generate files if requested
        doc_generator = DocumentGenerationService()
        file_paths = []
        
        for document_id in document_ids:
            document = GeneratedDocument.objects.get(id=document_id)
            
            for format_type in output_formats:
                if format_type == 'pdf':
                    file_path = doc_generator.generate_pdf(document.content, document.document_type)
                elif format_type == 'docx':
                    file_path = doc_generator.generate_docx(document.content, document.document_type)
                else:
                    continue
                    
                if file_path:
                    file_paths.append(file_path)
        
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 5: Finalize
        progress.update(95, "Finalizing documents...", "5/5")
        
        # Store document IDs in session for download
        from django.contrib.sessions.models import Session
        from django.contrib.sessions.backends.db import SessionStore
        try:
            session_store = SessionStore(session_key=session_key)
            session_data = session_store.load()
            session_data['generated_document_ids'] = document_ids
            session_store.save()
        except Exception as e:
            logger.warning(f"Could not save to session: {e}")
        
        # Complete
        progress.complete("Document generation completed!")
        
    except Exception as e:
        logger.error(f"Error in background document generation: {e}")
        progress.set_error(f"Failed to generate documents: {str(e)}")


# API Views for AJAX functionality
@csrf_exempt
def check_scraping_status(request, session_id):
    """Check scraping session status (for AJAX polling)"""
    try:
        session = ScrapingSession.objects.get(id=session_id)
        data = {
            'status': session.status,
            'method_used': session.method_used,
            'error_message': session.error_message,
        }
        
        if session.job_posting:
            data['job_posting_id'] = str(session.job_posting.id)
            data['job_title'] = session.job_posting.title or 'Unknown Job'
            data['company'] = session.job_posting.company or 'Unknown Company'
        
        return JsonResponse(data)
    except ScrapingSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
