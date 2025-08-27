"""
CV-First Enhancement Views
Implements comprehensive CV management functionality while preserving all existing features
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import uuid
import threading
import json
import logging

from .models import UserProfile, JobPosting, ProgressTask
from .forms import PersonalInfoForm, ProfessionalProfileForm, ResumeUploadForm, ComprehensiveCVForm
from .services.parsing_service import ResumeParsingService
from .utils import ProgressTracker, simulate_progress_delay

logger = logging.getLogger(__name__)


class CVDashboardView(TemplateView):
    """CV Dashboard showing profile completeness and quick actions"""
    template_name = 'jobassistant/cv_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user profile
        user_profile = self.get_user_profile()
        
        # Calculate profile completeness
        completeness_data = self.calculate_completeness(user_profile)
        
        # Get recent applications (job postings)
        recent_applications = JobPosting.objects.all()[:5] if user_profile else []
        
        # Get recent tasks/progress (general recent tasks since ProgressTask doesn't have user_profile field)
        recent_tasks = ProgressTask.objects.all().order_by('-created_at')[:5] if user_profile else []
        
        context.update({
            'user_profile': user_profile,
            'has_profile': bool(user_profile),
            'completeness': completeness_data,
            'recent_applications': recent_applications,
            'recent_tasks': recent_tasks,
        })
        
        return context
    
    def get_user_profile(self):
        """Get user profile from session or user"""
        if self.request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=self.request.user).first()
        else:
            session_key = self.request.session.session_key
            if session_key:
                profile = UserProfile.objects.filter(session_key=session_key).first()
            else:
                profile = None
        
        return profile
    
    def calculate_completeness(self, profile):
        """Calculate profile completeness percentage"""
        if not profile:
            return {
                'percentage': 0,
                'completed_fields': 0,
                'total_fields': 12,
                'missing_fields': [
                    'Personal Information', 'Professional Summary', 'Skills',
                    'Work Experience', 'Education'
                ]
            }
        
        # Essential fields for completeness (using new model structure)
        fields_to_check = [
            ('first_name', 'First Name'),
            ('last_name', 'Last Name'),
            ('email', 'Email'),
            ('mobile_phone', 'Mobile Phone'),
            ('city', 'City'),
            ('professional_summary', 'Professional Summary'),
            ('career_objectives', 'Career Objectives'),
            ('target_industry', 'Target Industry'),
            ('years_experience', 'Years of Experience'),
            ('employment_status', 'Employment Status'),
            ('linkedin_url', 'LinkedIn Profile'),
            ('availability', 'Availability'),
        ]
        
        completed_fields = 0
        missing_fields = []
        
        for field_name, display_name in fields_to_check:
            field_value = getattr(profile, field_name, '')
            if field_value and str(field_value).strip():
                completed_fields += 1
            else:
                missing_fields.append(display_name)
        
        # Check related models
        has_work_experience = profile.workexperience_set.exists()
        has_education = profile.education_set.exists()
        has_skills = profile.skill_set.exists()
        
        if has_work_experience:
            completed_fields += 1
        else:
            missing_fields.append('Work Experience')
            
        if has_education:
            completed_fields += 1
        else:
            missing_fields.append('Education')
            
        if has_skills:
            completed_fields += 1
        else:
            missing_fields.append('Skills')
        
        total_fields = len(fields_to_check) + 3  # +3 for related models
        percentage = int((completed_fields / total_fields) * 100)
        
        return {
            'percentage': percentage,
            'completed_fields': completed_fields,
            'total_fields': total_fields,
            'missing_fields': missing_fields
        }


class CVUploadView(TemplateView):
    """CV Upload with drag-and-drop interface and progress tracking"""
    template_name = 'jobassistant/cv_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_form'] = ResumeUploadForm()
        return context


class CVCreationWizardView(TemplateView):
    """5-step CV creation wizard"""
    template_name = 'jobassistant/cv_wizard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current step from URL parameter
        step = self.request.GET.get('step', '1')
        context['current_step'] = int(step)
        
        # Get existing profile for pre-population
        user_profile = self.get_user_profile()
        
        # Create appropriate form for the step
        if step == '1':
            # Personal Information
            context['form'] = PersonalInfoForm(instance=user_profile)
            context['step_title'] = 'Personal Information'
            context['step_description'] = 'Enter your contact details'
        elif step == '2':
            # Professional Summary
            context['form'] = ProfessionalProfileForm(instance=user_profile)
            context['step_title'] = 'Professional Summary'
            context['step_description'] = 'Describe your professional background'
        elif step == '3':
            # Skills
            context['form'] = PersonalInfoForm(instance=user_profile)  # Using PersonalInfoForm temporarily
            context['step_title'] = 'Skills & Expertise'
            context['step_description'] = 'List your technical and soft skills'
        elif step == '4':
            # Work Experience
            context['form'] = PersonalInfoForm(instance=user_profile)  # Using PersonalInfoForm temporarily
            context['step_title'] = 'Work Experience'
            context['step_description'] = 'Detail your professional experience'
        elif step == '5':
            # Education
            context['form'] = PersonalInfoForm(instance=user_profile)  # Using PersonalInfoForm temporarily
            context['step_title'] = 'Education & Certifications'
            context['step_description'] = 'Add your educational background'
        
        return context
    
    def get_user_profile(self):
        """Get user profile from session or user"""
        if self.request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=self.request.user).first()
        else:
            session_key = self.request.session.session_key
            if session_key:
                profile = UserProfile.objects.filter(session_key=session_key).first()
            else:
                profile = None
        return profile


class CVProfileView(TemplateView):
    """Beautiful, professional CV display"""
    template_name = 'jobassistant/cv_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        # Process skills for display
        technical_skills = user_profile.get_skills_list()
        soft_skills = user_profile.get_soft_skills_list()
        
        # Parse work experience for timeline display
        work_experience = self.parse_work_experience(user_profile.work_experience)
        
        # Parse education
        education = self.parse_education(user_profile.education)
        
        context.update({
            'profile': user_profile,
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'work_experience': work_experience,
            'education': education,
        })
        
        return context
    
    def parse_work_experience(self, experience_text):
        """Parse work experience text into structured format"""
        if not experience_text:
            return []
        
        # Split by double newlines or multiple newlines
        entries = [entry.strip() for entry in experience_text.split('\n\n') if entry.strip()]
        
        parsed_entries = []
        for entry in entries:
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            if lines:
                # First line usually contains title, company, dates
                header = lines[0]
                responsibilities = lines[1:] if len(lines) > 1 else []
                
                parsed_entries.append({
                    'header': header,
                    'responsibilities': responsibilities
                })
        
        return parsed_entries
    
    def parse_education(self, education_text):
        """Parse education text into structured format"""
        if not education_text:
            return []
        
        # Split by newlines
        entries = [entry.strip() for entry in education_text.split('\n') if entry.strip()]
        return entries


class CVEditView(TemplateView):
    """Form-based editing of comprehensive AU/NZ CV sections"""
    template_name = 'jobassistant/cv_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        # Prepare form with all comprehensive CV fields
        form = ComprehensiveCVForm(instance=user_profile)
        
        context.update({
            'profile': user_profile,
            'form': form,
            'visa_status_choices': UserProfile.VISA_STATUS_CHOICES,
            'availability_choices': UserProfile.AVAILABILITY_CHOICES,
            'references_choices': UserProfile.REFERENCES_CHOICE,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comprehensive CV edit form submission"""
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        # Handle file uploads if present
        files = request.FILES
        
        form = ComprehensiveCVForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            try:
                # Save the form
                updated_profile = form.save()
                
                # Add success message with details
                messages.success(
                    request, 
                    'Your professional CV has been updated successfully! All sections including personal details, '
                    'professional summary, skills, experience, education, and additional information have been saved.'
                )
                
                # Redirect to CV profile view
                return redirect('jobassistant:cv_profile', profile_id=profile_id)
                
            except Exception as e:
                logger.error(f"Error saving CV data for profile {profile_id}: {e}")
                messages.error(
                    request, 
                    'An error occurred while saving your CV. Please try again or contact support if the problem persists.'
                )
        else:
            # Form validation failed
            error_count = sum(len(errors) for errors in form.errors.values())
            messages.error(
                request, 
                f'Please correct {error_count} error(s) in your CV before saving. '
                'Check the highlighted fields below for specific requirements.'
            )
        
        # Render form with errors
        return render(request, self.template_name, {
            'profile': user_profile,
            'form': form,
            'visa_status_choices': UserProfile.VISA_STATUS_CHOICES,
            'availability_choices': UserProfile.AVAILABILITY_CHOICES,
            'references_choices': UserProfile.REFERENCES_CHOICE,
        })


# AJAX Endpoints for CV Wizard

@csrf_exempt
def save_wizard_step(request):
    """Save individual wizard step via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        step = data.get('step')
        form_data = data.get('form_data', {})
        
        # Get or create user profile
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'session_key': request.session.session_key or request.session.create()}
            )
        else:
            session_key = request.session.session_key or request.session.create()
            profile, created = UserProfile.objects.get_or_create(
                session_key=session_key,
                defaults={}
            )
        
        # Update profile based on step
        if step == 1:
            # Personal Information (AU/NZ CV Standards)
            profile.full_name = form_data.get('full_name', profile.full_name)
            profile.email = form_data.get('email', profile.email)
            profile.phone = form_data.get('phone', profile.phone)
            profile.city_region = form_data.get('city_region', profile.city_region)
            profile.linkedin_url = form_data.get('linkedin_url', profile.linkedin_url)
            profile.portfolio_url = form_data.get('portfolio_url', profile.portfolio_url)
            
            # AU/NZ Specific Fields
            profile.visa_work_rights = form_data.get('visa_work_rights', profile.visa_work_rights)
            profile.availability = form_data.get('availability', profile.availability)
            profile.drivers_license = form_data.get('drivers_license', profile.drivers_license) == 'true'
        
        elif step == 2:
            # Professional Summary
            profile.professional_summary = form_data.get('professional_summary', profile.professional_summary)
            profile.experience_level = form_data.get('experience_level', profile.experience_level)
        
        elif step == 3:
            # Skills (Technical & Soft Skills)
            profile.technical_skills = form_data.get('technical_skills', profile.technical_skills)
            profile.soft_skills = form_data.get('soft_skills', profile.soft_skills)
            profile.languages = form_data.get('languages', profile.languages)
        
        elif step == 4:
            # Work Experience
            profile.work_experience = form_data.get('work_experience', profile.work_experience)
        
        elif step == 5:
            # Education
            profile.education = form_data.get('education', profile.education)
        
        elif step == 6:
            # Certifications & Professional Development
            profile.certifications = form_data.get('certifications', profile.certifications)
            profile.professional_memberships = form_data.get('professional_memberships', profile.professional_memberships)
        
        elif step == 7:
            # Projects & Achievements
            profile.projects = form_data.get('projects', profile.projects)
            profile.achievements = form_data.get('achievements', profile.achievements)
        
        elif step == 8:
            # Volunteer Work & Additional Information
            profile.volunteer_work = form_data.get('volunteer_work', profile.volunteer_work)
        
        elif step == 9:
            # References
            profile.references_choice = form_data.get('references_choice', profile.references_choice)
            if profile.references_choice == 'provided':
                profile.references = form_data.get('references', profile.references)
        
        profile.save()
        
        # Store profile ID in session
        request.session['user_profile_id'] = str(profile.id)
        
        return JsonResponse({
            'success': True,
            'profile_id': str(profile.id),
            'message': f'Step {step} saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving wizard step: {e}")
        return JsonResponse({
            'error': f'Failed to save step: {str(e)}'
        }, status=400)


@csrf_exempt
def upload_cv_with_progress(request):
    """Upload CV file with progress tracking"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    if 'cv_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['cv_file']
    
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
        target=_parse_cv_background,
        args=(task_id, file_content, file_name, request.session.session_key, request.user.id if request.user.is_authenticated else None)
    )
    thread.daemon = True
    thread.start()
    
    return JsonResponse({
        'success': True,
        'task_id': task_id,
        'message': 'CV upload started'
    })


def _parse_cv_background(task_id, file_content, file_name, session_key, user_id=None):
    """Background task for CV parsing with progress updates"""
    progress = ProgressTracker(task_id)
    
    try:
        # Stage 1: Upload file
        progress.update(10, "Uploading CV...", "1/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 2: Validate file format
        progress.update(25, "Validating file format...", "2/6")
        simulate_progress_delay(0.5, 1.0)
        
        # Stage 3: Extract text content
        progress.update(45, "Extracting content...", "3/6")
        
        # Create a temporary file-like object for parsing
        from io import BytesIO
        file_obj = BytesIO(file_content)
        file_obj.name = file_name
        
        # Use existing parsing service
        app_version = getattr(settings, 'APP_VERSION', 'free')
        use_paid = app_version == 'paid'
        parser = ResumeParsingService(use_paid_apis=use_paid)
        
        # Create a mock UploadedFile-like object for compatibility
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Reset file position
        file_obj.seek(0)
        file_content = file_obj.read()
        
        # Create proper UploadedFile
        uploaded_file = SimpleUploadedFile(
            name=file_name,
            content=file_content,
            content_type='application/pdf' if file_name.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        parsed_data = parser.parse_resume(uploaded_file)
        simulate_progress_delay(2.0, 4.0)
        
        # Stage 4: Parse sections
        progress.update(65, "Parsing CV sections...", "4/6")
        simulate_progress_delay(1.5, 3.0)
        
        # Stage 5: Structure data
        progress.update(85, "Structuring data...", "5/6")
        simulate_progress_delay(1.0, 2.0)
        
        # Stage 6: Save profile
        progress.update(95, "Finalizing CV profile...", "6/6")
        
        # Create or update UserProfile
        if user_id:
            # Authenticated user
            profile, created = UserProfile.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'session_key': session_key,
                    'full_name': parsed_data.get('full_name', ''),
                    'email': parsed_data.get('email', ''),
                    'phone': parsed_data.get('phone', ''),
                    'city_region': parsed_data.get('location', ''),
                    'linkedin_url': parsed_data.get('linkedin_url', ''),
                    'portfolio_url': parsed_data.get('portfolio_url', ''),
                    'professional_summary': parsed_data.get('professional_summary', ''),
                    'technical_skills': parsed_data.get('technical_skills', ''),
                    'soft_skills': parsed_data.get('soft_skills', ''),
                    'certifications': parsed_data.get('certifications', ''),
                    'education': parsed_data.get('education', ''),
                    'work_experience': parsed_data.get('work_experience', ''),
                    'achievements': parsed_data.get('achievements', ''),
                    'parsed_content': parsed_data.get('raw_text', '')
                }
            )
            if not created:
                # Update existing profile
                for field, value in {
                    'full_name': parsed_data.get('full_name', ''),
                    'email': parsed_data.get('email', ''),
                    'phone': parsed_data.get('phone', ''),
                    'city_region': parsed_data.get('location', ''),
                    'linkedin_url': parsed_data.get('linkedin_url', ''),
                    'portfolio_url': parsed_data.get('portfolio_url', ''),
                    'professional_summary': parsed_data.get('professional_summary', ''),
                    'technical_skills': parsed_data.get('technical_skills', ''),
                    'soft_skills': parsed_data.get('soft_skills', ''),
                    'certifications': parsed_data.get('certifications', ''),
                    'education': parsed_data.get('education', ''),
                    'work_experience': parsed_data.get('work_experience', ''),
                    'achievements': parsed_data.get('achievements', ''),
                    'parsed_content': parsed_data.get('raw_text', '')
                }.items():
                    if value:  # Only update if we have data
                        setattr(profile, field, value)
                profile.save()
        else:
            # Anonymous user
            profile, created = UserProfile.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'full_name': parsed_data.get('full_name', ''),
                    'email': parsed_data.get('email', ''),
                    'phone': parsed_data.get('phone', ''),
                    'city_region': parsed_data.get('location', ''),
                    'linkedin_url': parsed_data.get('linkedin_url', ''),
                    'portfolio_url': parsed_data.get('portfolio_url', ''),
                    'professional_summary': parsed_data.get('professional_summary', ''),
                    'technical_skills': parsed_data.get('technical_skills', ''),
                    'soft_skills': parsed_data.get('soft_skills', ''),
                    'certifications': parsed_data.get('certifications', ''),
                    'education': parsed_data.get('education', ''),
                    'work_experience': parsed_data.get('work_experience', ''),
                    'achievements': parsed_data.get('achievements', ''),
                    'parsed_content': parsed_data.get('raw_text', '')
                }
            )
        
        progress.update(100, "CV uploaded successfully!", "Complete")
        progress.complete("CV uploaded successfully!", {
            'profile_id': str(profile.id),
            'profile_url': f'/cv/profile/{profile.id}/',
            'edit_url': f'/cv/edit/{profile.id}/',
            'success': True
        })
        
    except Exception as e:
        error_msg = f"CV parsing failed: {str(e)}"
        logger.error(error_msg)
        progress.set_error(error_msg)


