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
    """Handle job URL scraping"""
    if request.method == 'POST':
        form = JobURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Create scraping session
            session = ScrapingSession.objects.create(
                url=url,
                status='in_progress'
            )
            
            try:
                # Determine if we should use paid APIs
                app_version = getattr(settings, 'APP_VERSION', 'free')
                use_paid = app_version == 'paid'
                
                # Initialize scraping service
                scraper = JobScrapingService(use_paid_apis=use_paid)
                
                # Scrape the job
                job_data, method_used = scraper.scrape_job(url)
                
                if job_data and job_data.get('title'):
                    # Create job posting
                    job_posting = JobPosting.objects.create(
                        url=url,
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
                    
                    # Update session
                    session.job_posting = job_posting
                    session.status = 'success'
                    session.method_used = method_used
                    session.completed_at = timezone.now()
                    session.save()
                    
                    # Store job ID in session
                    request.session['job_posting_id'] = str(job_posting.id)
                    
                    messages.success(request, f'Successfully scraped job posting: {job_posting.title}')
                    return redirect('jobassistant:job_details', job_id=job_posting.id)
                    
                else:
                    session.status = 'failed'
                    session.error_message = 'Could not extract job information from URL'
                    session.completed_at = timezone.now()
                    session.save()
                    
                    messages.error(request, 'Could not extract job information from the provided URL. Please try a different URL or enter the information manually.')
                    
            except Exception as e:
                session.status = 'failed'
                session.error_message = str(e)
                session.completed_at = timezone.now()
                session.save()
                
                logger.error(f"Error scraping job URL {url}: {str(e)}")
                messages.error(request, f'Error scraping job posting: {str(e)}')
        
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
            data['job_title'] = session.job_posting.title
            data['company'] = session.job_posting.company
        
        return JsonResponse(data)
    except ScrapingSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
