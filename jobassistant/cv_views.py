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

from .models import UserProfile, JobPosting, GeneratedDocument
from .forms import UserProfileForm, ResumeUploadForm
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
        
        # Get generated documents
        recent_documents = GeneratedDocument.objects.filter(
            user_profile=user_profile
        )[:5] if user_profile else []
        
        context.update({
            'user_profile': user_profile,
            'has_profile': bool(user_profile),
            'completeness': completeness_data,
            'recent_applications': recent_applications,
            'recent_documents': recent_documents,
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
        
        # Essential fields for completeness
        fields_to_check = [
            ('full_name', 'Full Name'),
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('location', 'Location'),
            ('professional_summary', 'Professional Summary'),
            ('technical_skills', 'Technical Skills'),
            ('soft_skills', 'Soft Skills'),
            ('work_experience', 'Work Experience'),
            ('education', 'Education'),
            ('experience_level', 'Experience Level'),
            ('linkedin_url', 'LinkedIn Profile'),
            ('achievements', 'Achievements'),
        ]
        
        completed_fields = 0
        missing_fields = []
        
        for field_name, display_name in fields_to_check:
            field_value = getattr(profile, field_name, '')
            if field_value and str(field_value).strip():
                completed_fields += 1
            else:
                missing_fields.append(display_name)
        
        total_fields = len(fields_to_check)
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
            context['form'] = ProfessionalSummaryForm(instance=user_profile)
            context['step_title'] = 'Professional Summary'
            context['step_description'] = 'Describe your professional background'
        elif step == '3':
            # Skills
            context['form'] = SkillsForm(instance=user_profile)
            context['step_title'] = 'Skills & Expertise'
            context['step_description'] = 'List your technical and soft skills'
        elif step == '4':
            # Work Experience
            context['form'] = WorkExperienceForm(instance=user_profile)
            context['step_title'] = 'Work Experience'
            context['step_description'] = 'Detail your professional experience'
        elif step == '5':
            # Education
            context['form'] = EducationForm(instance=user_profile)
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
    """Form-based editing of CV sections"""
    template_name = 'jobassistant/cv_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        context.update({
            'profile': user_profile,
            'form': UserProfileForm(instance=user_profile),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle CV edit form submission"""
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('jobassistant:cv_profile', profile_id=profile_id)
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {
                'profile': user_profile,
                'form': form,
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
            # Personal Information
            profile.full_name = form_data.get('full_name', profile.full_name)
            profile.email = form_data.get('email', profile.email)
            profile.phone = form_data.get('phone', profile.phone)
            profile.location = form_data.get('location', profile.location)
            profile.linkedin_url = form_data.get('linkedin_url', profile.linkedin_url)
            profile.portfolio_url = form_data.get('portfolio_url', profile.portfolio_url)
        
        elif step == 2:
            # Professional Summary
            profile.professional_summary = form_data.get('professional_summary', profile.professional_summary)
            profile.experience_level = form_data.get('experience_level', profile.experience_level)
        
        elif step == 3:
            # Skills
            profile.technical_skills = form_data.get('technical_skills', profile.technical_skills)
            profile.soft_skills = form_data.get('soft_skills', profile.soft_skills)
            profile.certifications = form_data.get('certifications', profile.certifications)
        
        elif step == 4:
            # Work Experience
            profile.work_experience = form_data.get('work_experience', profile.work_experience)
            profile.achievements = form_data.get('achievements', profile.achievements)
        
        elif step == 5:
            # Education
            profile.education = form_data.get('education', profile.education)
        
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
                    'location': parsed_data.get('location', ''),
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
                    'location': parsed_data.get('location', ''),
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
                    'location': parsed_data.get('location', ''),
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


# Forms for CV Wizard Steps
from django import forms

class PersonalInfoForm(forms.ModelForm):
    """Form for personal information step"""
    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'phone', 'location', 'linkedin_url', 'portfolio_url']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.doe@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/johndoe'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://johndoe.com'}),
        }


class ProfessionalSummaryForm(forms.ModelForm):
    """Form for professional summary step"""
    class Meta:
        model = UserProfile
        fields = ['professional_summary', 'experience_level']
        widgets = {
            'professional_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief summary of your professional background and key achievements...'
            }),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
        }


class SkillsForm(forms.ModelForm):
    """Form for skills step"""
    class Meta:
        model = UserProfile
        fields = ['technical_skills', 'soft_skills', 'certifications']
        widgets = {
            'technical_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, JavaScript, React, Django, SQL, AWS (comma-separated)'
            }),
            'soft_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Leadership, Communication, Problem-solving, Team collaboration (comma-separated)'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List your relevant certifications, licenses, and credentials...'
            }),
        }


class WorkExperienceForm(forms.ModelForm):
    """Form for work experience step"""
    class Meta:
        model = UserProfile
        fields = ['work_experience', 'achievements']
        widgets = {
            'work_experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Job Title | Company | Dates\n• Key responsibility or achievement\n• Another key responsibility...'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notable achievements, awards, projects, or quantifiable results...'
            }),
        }


class EducationForm(forms.ModelForm):
    """Form for education step"""
    class Meta:
        model = UserProfile
        fields = ['education']
        widgets = {
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Degree, Institution, Year\nMajor achievements or relevant coursework...'
            }),
        }
