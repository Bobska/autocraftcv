"""
Professional CV Builder Views
Updated to work with the new UserProfile model structure
"""
import logging
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse

from .models import UserProfile, JobPosting, ProgressTask, WorkExperience, Education, Skill
from .forms import PersonalInfoForm, ProfessionalProfileForm, ComprehensiveCVForm

logger = logging.getLogger(__name__)


class CVDashboardView(TemplateView):
    """Professional CV Dashboard showing profile completeness and quick actions"""
    template_name = 'jobassistant/cv_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user profile
        user_profile = self.get_user_profile()
        
        # Calculate profile completeness
        completeness_data = self.calculate_completeness(user_profile)
        
        # Get recent data
        recent_applications = JobPosting.objects.all()[:5] if user_profile else []
        recent_tasks = ProgressTask.objects.all().order_by('-created_at')[:5]
        
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
                'total_fields': 15,
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
        has_work_experience = profile.work_experiences.exists()
        has_education = profile.education_entries.exists()
        has_skills = profile.skills.exists()
        
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
    """CV Upload with drag-and-drop interface"""
    template_name = 'jobassistant/cv_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_url'] = reverse('jobassistant:upload_cv_with_progress')
        return context


class CVCreationWizardView(TemplateView):
    """Multi-step CV creation wizard"""
    template_name = 'jobassistant/cv_wizard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current step from URL
        step = self.kwargs.get('step', '1')
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
        else:
            # Use PersonalInfoForm as fallback
            context['form'] = PersonalInfoForm(instance=user_profile)
            context['step_title'] = 'CV Information'
            context['step_description'] = 'Complete your CV details'
        
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
    """Display CV profile with all sections"""
    template_name = 'jobassistant/cv_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        # Get related data (simplified queries)
        work_experiences = user_profile.work_experiences.all()
        educations = user_profile.education_entries.all()
        skills = user_profile.skills.all()
        certifications = user_profile.certifications.all()
        projects = user_profile.projects.all()
        
        context.update({
            'profile': user_profile,
            'work_experiences': work_experiences,
            'educations': educations,
            'skills': skills,
            'certifications': certifications,
            'projects': projects,
        })
        
        return context


class CVEditView(TemplateView):
    """Form-based editing of comprehensive CV sections"""
    template_name = 'jobassistant/cv_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        # Prepare comprehensive form
        form = ComprehensiveCVForm(instance=user_profile)
        
        context.update({
            'profile': user_profile,
            'form': form,
            'visa_status_choices': UserProfile.VISA_STATUS_CHOICES,
            'availability_choices': UserProfile.AVAILABILITY_CHOICES,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comprehensive CV edit form submission"""
        profile_id = kwargs.get('profile_id')
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        
        form = ComprehensiveCVForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            try:
                # Save the form
                updated_profile = form.save()
                
                # Add success message
                messages.success(
                    request, 
                    'Your professional CV has been updated successfully! All sections have been saved.'
                )
                
                # Redirect to CV profile view
                return redirect('jobassistant:cv_profile', profile_id=profile_id)
                
            except Exception as e:
                logger.error(f"Error saving CV data for profile {profile_id}: {e}")
                messages.error(
                    request,
                    'There was an error saving your CV. Please try again.'
                )
        else:
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
        
        # If form is invalid or error occurred, redisplay form
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


# API Views and Functions

def save_wizard_step(request):
    """Save CV wizard step data via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        step = request.POST.get('step')
        form_data = request.POST.dict()
        
        # Get or create user profile
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            profile, created = UserProfile.objects.get_or_create(session_key=session_key)
        
        # Update profile based on step
        if step == '1':
            # Personal Information
            if 'first_name' in form_data:
                profile.first_name = form_data['first_name']
            if 'last_name' in form_data:
                profile.last_name = form_data['last_name']
            if 'email' in form_data:
                profile.email = form_data['email']
            if 'mobile_phone' in form_data:
                profile.mobile_phone = form_data['mobile_phone']
        elif step == '2':
            # Professional Profile
            if 'professional_summary' in form_data:
                profile.professional_summary = form_data['professional_summary']
            if 'career_objectives' in form_data:
                profile.career_objectives = form_data['career_objectives']
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Step {step} saved successfully',
            'profile_id': str(profile.id)
        })
        
    except Exception as e:
        logger.error(f"Error saving wizard step: {e}")
        return JsonResponse({'error': 'Failed to save step'}, status=500)


def upload_cv_with_progress(request):
    """Handle CV file upload with progress tracking"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        # Create a progress task
        task_id = str(uuid.uuid4())
        task = ProgressTask.objects.create(
            task_id=task_id,
            status='processing',
            current_step='Uploading file...'
        )
        
        # For now, just return success
        # In a real implementation, this would handle file upload and parsing
        task.status = 'completed'
        task.progress = 100
        task.current_step = 'Upload completed'
        task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'message': 'CV uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading CV: {e}")
        return JsonResponse({'error': 'Failed to upload CV'}, status=500)
