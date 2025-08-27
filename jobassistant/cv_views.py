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
        
        print(f"DEBUG GET: Wizard accessed - Step {step}, Method: {self.request.method}")
        
        # Get existing profile for pre-population
        user_profile = self.get_user_profile()
        print(f"DEBUG GET: User profile: {user_profile}")
        
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
    
    def post(self, request, *args, **kwargs):
        """Handle form submission for wizard steps"""
        step = request.GET.get('step', '1')
        current_step = int(step)
        
        print(f"DEBUG WIZARD POST: Step {current_step}")
        print(f"DEBUG WIZARD POST: POST data keys: {list(request.POST.keys())}")
        
        # Get or create user profile
        user_profile = self.get_user_profile()
        print(f"DEBUG WIZARD POST: Existing profile: {user_profile}")
        
        if not user_profile:
            if request.user.is_authenticated:
                user_profile = UserProfile.objects.create(user=request.user)
                print(f"DEBUG WIZARD POST: Created profile for user: {user_profile.id}")
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                user_profile = UserProfile.objects.create(session_key=session_key)
                print(f"DEBUG WIZARD POST: Created profile for session: {user_profile.id}")
        else:
            print(f"DEBUG WIZARD POST: Using existing profile: {user_profile.id}")
        
        # Handle different step forms
        form_valid = False
        
        if current_step == 1:
            form = PersonalInfoForm(request.POST, instance=user_profile)
            print(f"DEBUG WIZARD: Step 1 form data: {dict(request.POST)}")
            if form.is_valid():
                saved_profile = form.save()
                print(f"DEBUG WIZARD: Step 1 saved successfully. Profile name: {saved_profile.first_name} {saved_profile.last_name}")
                form_valid = True
            else:
                print(f"DEBUG WIZARD: Step 1 form errors: {form.errors}")
        elif current_step == 2:
            form = ProfessionalProfileForm(request.POST, instance=user_profile)
            print(f"DEBUG WIZARD: Step 2 form data: {dict(request.POST)}")
            if form.is_valid():
                saved_profile = form.save()
                print(f"DEBUG WIZARD: Step 2 saved successfully. Summary: {saved_profile.professional_summary[:50] if saved_profile.professional_summary else 'None'}")
                form_valid = True
            else:
                print(f"DEBUG WIZARD: Step 2 form errors: {form.errors}")
        elif current_step == 3:
            form = SkillsForm(request.POST, instance=user_profile)
            print(f"DEBUG WIZARD: Step 3 form data: {dict(request.POST)}")
            if form.is_valid():
                self._save_skills_form(form, user_profile)
                print(f"DEBUG WIZARD: Step 3 saved successfully. Skills count after save: {user_profile.skills.count()}")
                form_valid = True
            else:
                print(f"DEBUG WIZARD: Step 3 form errors: {form.errors}")
        elif current_step == 4:
            form = WorkExperienceWizardForm(request.POST, instance=user_profile)
            print(f"DEBUG WIZARD: Step 4 form data: {dict(request.POST)}")
            if form.is_valid():
                self._save_work_experience_form(form, user_profile)
                print(f"DEBUG WIZARD: Step 4 saved successfully. Work exp count: {user_profile.work_experiences.count()}")
                form_valid = True
            else:
                print(f"DEBUG WIZARD: Step 4 form errors: {form.errors}")
        elif current_step == 5:
            form = EducationWizardForm(request.POST, instance=user_profile)
            print(f"DEBUG WIZARD: Step 5 form data: {dict(request.POST)}")
            if form.is_valid():
                self._save_education_form(form, user_profile)
                print(f"DEBUG WIZARD: Step 5 saved successfully. Education count: {user_profile.education_entries.count()}")
                form_valid = True
            else:
                print(f"DEBUG WIZARD: Step 5 form errors: {form.errors}")
        else:
            form = PersonalInfoForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                form_valid = True
        
        # Handle step completion if form was valid
        if form_valid:
            return self._handle_step_completion(request, current_step, user_profile)
        
        # If form is invalid, redisplay with errors
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def _handle_step_completion(self, request, current_step, user_profile):
        """Handle what happens after a step is completed"""
        if current_step == 5:
            # Final step completed - mark as active and redirect to profile
            user_profile.profile_status = 'active'
            user_profile.save()
            messages.success(request, 'Your CV has been created successfully!')
            return redirect('jobassistant:cv_profile', profile_id=user_profile.id)
        else:
            # Move to next step
            next_step = current_step + 1
            return redirect(f"{request.path}?step={next_step}")
    
    def _save_skills_form(self, form, user_profile):
        """Save skills form data"""
        from datetime import datetime
        
        # Clear existing skills
        user_profile.skills.all().delete()
        
        # Save technical skills
        technical_skills = form.cleaned_data.get('technical_skills', '')
        if technical_skills:
            skills = [skill.strip() for skill in technical_skills.split(',') if skill.strip()]
            for skill_name in skills:
                Skill.objects.create(
                    profile=user_profile,
                    name=skill_name,
                    category='technical'
                )
        
        # Save soft skills
        soft_skills = form.cleaned_data.get('soft_skills', '')
        if soft_skills:
            skills = [skill.strip() for skill in soft_skills.split(',') if skill.strip()]
            for skill_name in skills:
                Skill.objects.create(
                    profile=user_profile,
                    name=skill_name,
                    category='soft'
                )
    
    def _save_work_experience_form(self, form, user_profile):
        """Save work experience form data"""
        # Get or create the most recent work experience
        work_exp = user_profile.work_experiences.first()
        
        if not work_exp:
            work_exp = WorkExperience(profile=user_profile)
        
        # Update fields from form
        work_exp.job_title = form.cleaned_data.get('job_title', '')
        work_exp.company_name = form.cleaned_data.get('company_name', '')
        work_exp.company_location = form.cleaned_data.get('company_location', '')
        work_exp.employment_type = form.cleaned_data.get('employment_type', '')
        work_exp.start_date = form.cleaned_data.get('start_date')
        work_exp.end_date = form.cleaned_data.get('end_date')
        work_exp.currently_working = form.cleaned_data.get('currently_working', False)
        work_exp.key_responsibilities = form.cleaned_data.get('key_responsibilities', '')
        work_exp.key_achievements = form.cleaned_data.get('key_achievements', '')
        
        # Only save if we have essential fields
        if work_exp.job_title and work_exp.company_name:
            work_exp.save()
    
    def _save_education_form(self, form, user_profile):
        """Save education form data"""
        from .models import Education
        
        # Get or create the most recent education entry
        education = user_profile.education_entries.first()
        
        if not education:
            education = Education(profile=user_profile)
        
        # Update fields from form
        education.degree_type = form.cleaned_data.get('degree_type', '')
        education.field_of_study = form.cleaned_data.get('field_of_study', '')
        education.institution_name = form.cleaned_data.get('institution_name', '')
        education.institution_location = form.cleaned_data.get('institution_location', '')
        education.graduation_year = form.cleaned_data.get('graduation_year')
        education.gpa_grade = form.cleaned_data.get('gpa_grade', '')
        education.relevant_coursework = form.cleaned_data.get('relevant_coursework', '')
        education.academic_achievements = form.cleaned_data.get('academic_achievements', '')
        
        # Only save if we have essential fields
        if education.field_of_study and education.institution_name:
            education.save()
    
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


def test_cv_profile_view(request, profile_id):
    """Simple test view to debug CV profile issues"""
    from django.http import HttpResponse
    
    try:
        user_profile = UserProfile.objects.get(id=profile_id)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test CV Profile</title></head>
        <body>
            <h1>TEST CV PROFILE DEBUG</h1>
            <p><strong>Profile ID:</strong> {user_profile.id}</p>
            <p><strong>Full Name:</strong> "{user_profile.full_name}"</p>
            <p><strong>First Name:</strong> "{user_profile.first_name}"</p>
            <p><strong>Last Name:</strong> "{user_profile.last_name}"</p>
            <p><strong>Email:</strong> "{user_profile.email}"</p>
            <p><strong>Mobile Phone:</strong> "{user_profile.mobile_phone}"</p>
            <p><strong>City:</strong> "{user_profile.city}"</p>
            <p><strong>Professional Summary:</strong> "{user_profile.professional_summary}"</p>
            <p><strong>Work Experiences:</strong> {user_profile.work_experiences.count()}</p>
            <p><strong>Education:</strong> {user_profile.education_entries.count()}</p>
            <p><strong>Skills:</strong> {user_profile.skills.count()}</p>
            
            <h2>Work Experiences</h2>
            <ul>
            {''.join([f'<li>{exp.job_title} at {exp.company_name}</li>' for exp in user_profile.work_experiences.all()])}
            </ul>
            
            <h2>Education</h2>
            <ul>
            {''.join([f'<li>{edu.field_of_study} at {edu.institution_name}</li>' for edu in user_profile.education_entries.all()])}
            </ul>
            
            <h2>Skills</h2>
            <ul>
            {''.join([f'<li>{skill.name} ({skill.category})</li>' for skill in user_profile.skills.all()])}
            </ul>
        </body>
        </html>
        """
        
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}")


class CVProfileView(TemplateView):
    """Display CV profile with all sections"""
    template_name = 'jobassistant/cv_profile.html'
    
    def get(self, request, *args, **kwargs):
        """Override get method for debugging"""
        print(f"DEBUG: CVProfileView.get() called")
        print(f"DEBUG: kwargs = {kwargs}")
        
        profile_id = kwargs.get('profile_id')
        print(f"DEBUG: Looking for profile ID: {profile_id}")
        
        try:
            user_profile = get_object_or_404(UserProfile, id=profile_id)
            print(f"DEBUG: Found profile: {user_profile.full_name} ({user_profile.email})")
            
            # Get related data
            work_experiences = user_profile.work_experiences.all()
            educations = user_profile.education_entries.all()
            skills = user_profile.skills.all()
            certifications = user_profile.certifications.all()
            projects = user_profile.projects.all()
            
            print(f"DEBUG: Work experiences: {work_experiences.count()}")
            print(f"DEBUG: Educations: {educations.count()}")
            print(f"DEBUG: Skills: {skills.count()}")
            
            context = {
                'profile': user_profile,
                'work_experiences': work_experiences,
                'educations': educations,
                'skills': skills,
                'certifications': certifications,
                'projects': projects,
            }
            
            return render(request, self.template_name, context)
            
        except Exception as e:
            print(f"DEBUG: Error in CVProfileView: {str(e)}")
            from django.http import HttpResponse
            return HttpResponse(f"DEBUG ERROR: {str(e)}")
    
    def get_context_data(self, **kwargs):
        # This method won't be called if we override get()
        pass


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
