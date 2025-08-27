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
from .forms import (
    PersonalInfoForm, ProfessionalProfileForm, ComprehensiveCVForm, 
    SkillsForm, WorkExperienceWizardForm, EducationWizardForm
)

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
        
        # Get current step from URL query parameter
        step = self.request.GET.get('step', '1')
        context['current_step'] = int(step)
        
        # Get existing profile for pre-population
        user_profile = self.get_user_profile()
        
        # Create appropriate form for the step
        if step == '1':
            # Personal Information
            context['form'] = PersonalInfoForm(instance=user_profile)
            context['step_title'] = 'Personal Information'
            context['step_description'] = 'Enter your contact details and basic information'
        elif step == '2':
            # Professional Summary
            context['form'] = ProfessionalProfileForm(instance=user_profile)
            context['step_title'] = 'Professional Summary'
            context['step_description'] = 'Describe your professional background and goals'
        elif step == '3':
            # Skills
            context['form'] = SkillsForm(instance=user_profile)
            context['step_title'] = 'Skills & Expertise'
            context['step_description'] = 'List your technical and soft skills'
        elif step == '4':
            # Work Experience
            context['form'] = WorkExperienceWizardForm(instance=user_profile)
            context['step_title'] = 'Work Experience'
            context['step_description'] = 'Add your work history and achievements'
        elif step == '5':
            # Education
            context['form'] = EducationWizardForm(instance=user_profile)
            context['step_title'] = 'Education & Qualifications'
            context['step_description'] = 'Add your educational background'
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
        import json
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            step = data.get('step')
            form_data = data.get('form_data', {})
            save_as_draft = data.get('save_as_draft', False)
        else:
            step = request.POST.get('step')
            form_data = request.POST.dict()
            save_as_draft = request.POST.get('save_as_draft', False)
        
        # Get or create user profile
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            profile, created = UserProfile.objects.get_or_create(session_key=session_key)
        
        # Set profile status based on save type
        if save_as_draft:
            profile.profile_status = 'draft'
        else:
            profile.profile_status = 'active'
        
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
            if 'address_line_1' in form_data:
                profile.address_line_1 = form_data['address_line_1']
            if 'city' in form_data:
                profile.city = form_data['city']
            if 'state_region' in form_data:
                profile.state_region = form_data['state_region']
            if 'country' in form_data:
                profile.country = form_data['country']
            if 'linkedin_url' in form_data:
                profile.linkedin_url = form_data['linkedin_url']
                
        elif step == '2':
            # Professional Profile
            if 'professional_summary' in form_data:
                profile.professional_summary = form_data['professional_summary']
            if 'career_objectives' in form_data:
                profile.career_objectives = form_data['career_objectives']
            if 'experience_level' in form_data:
                profile.experience_level = form_data['experience_level']
                
        elif step == '3':
            # Skills - handle as related model
            if 'technical_skills' in form_data:
                # Parse comma-separated skills and create Skill objects
                tech_skills = [skill.strip() for skill in form_data['technical_skills'].split(',') if skill.strip()]
                # Remove existing technical skills
                profile.skills.filter(category='technical').delete()
                # Create new technical skills
                for skill_name in tech_skills:
                    Skill.objects.create(
                        profile=profile,
                        name=skill_name,
                        category='technical'
                    )
                    
            if 'soft_skills' in form_data:
                # Parse comma-separated skills and create Skill objects
                soft_skills = [skill.strip() for skill in form_data['soft_skills'].split(',') if skill.strip()]
                # Remove existing soft skills
                profile.skills.filter(category='soft').delete()
                # Create new soft skills
                for skill_name in soft_skills:
                    Skill.objects.create(
                        profile=profile,
                        name=skill_name,
                        category='soft'
                    )
                    
        elif step == '4':
            # Work Experience - create or update the most recent entry
            if any(key in form_data for key in ['job_title', 'company_name', 'start_date']):
                # Get or create the most recent work experience
                work_exp = profile.work_experiences.first()
                
                if not work_exp:
                    work_exp = WorkExperience(profile=profile)
                
                # Update fields if provided
                if 'job_title' in form_data and form_data['job_title']:
                    work_exp.job_title = form_data['job_title']
                if 'company_name' in form_data and form_data['company_name']:
                    work_exp.company_name = form_data['company_name']
                if 'company_location' in form_data and form_data['company_location']:
                    work_exp.company_location = form_data['company_location']
                if 'employment_type' in form_data and form_data['employment_type']:
                    work_exp.employment_type = form_data['employment_type']
                if 'start_date' in form_data and form_data['start_date']:
                    try:
                        from datetime import datetime
                        work_exp.start_date = datetime.strptime(form_data['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Invalid date format, skip
                if 'end_date' in form_data and form_data['end_date']:
                    try:
                        from datetime import datetime
                        work_exp.end_date = datetime.strptime(form_data['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Invalid date format, skip
                if 'currently_working' in form_data:
                    work_exp.currently_working = bool(form_data['currently_working'])
                if 'key_responsibilities' in form_data and form_data['key_responsibilities']:
                    work_exp.key_responsibilities = form_data['key_responsibilities']
                if 'key_achievements' in form_data and form_data['key_achievements']:
                    work_exp.key_achievements = form_data['key_achievements']
                
                # Only save if we have essential fields
                if hasattr(work_exp, 'job_title') and hasattr(work_exp, 'company_name'):
                    work_exp.save()
                    
        elif step == '5':
            # Education - create or update the most recent entry
            if any(key in form_data for key in ['degree_type', 'field_of_study', 'institution_name']):
                # Get or create the most recent education entry
                education = profile.education_entries.first()
                
                if not education:
                    education = Education(profile=profile)
                
                # Update fields if provided
                if 'degree_type' in form_data and form_data['degree_type']:
                    education.degree_type = form_data['degree_type']
                if 'field_of_study' in form_data and form_data['field_of_study']:
                    education.field_of_study = form_data['field_of_study']
                if 'institution_name' in form_data and form_data['institution_name']:
                    education.institution_name = form_data['institution_name']
                if 'institution_location' in form_data and form_data['institution_location']:
                    education.institution_location = form_data['institution_location']
                if 'graduation_year' in form_data and form_data['graduation_year']:
                    try:
                        education.graduation_year = int(form_data['graduation_year'])
                    except ValueError:
                        pass  # Invalid year, skip
                if 'gpa_grade' in form_data and form_data['gpa_grade']:
                    education.gpa_grade = form_data['gpa_grade']
                if 'relevant_coursework' in form_data and form_data['relevant_coursework']:
                    education.relevant_coursework = form_data['relevant_coursework']
                if 'academic_achievements' in form_data and form_data['academic_achievements']:
                    education.academic_achievements = form_data['academic_achievements']
                
                # Only save if we have essential fields
                if hasattr(education, 'field_of_study') and hasattr(education, 'institution_name'):
                    education.save()
        
        profile.save()
        
        status_message = 'Draft saved successfully' if save_as_draft else f'Step {step} saved successfully'
        
        return JsonResponse({
            'success': True,
            'message': status_message,
            'profile_id': str(profile.id),
            'is_draft': save_as_draft
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
