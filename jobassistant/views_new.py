from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.db import transaction
import uuid

from .models import UserProfile, ProgressTask
from .forms import (
    PersonalInfoForm, ProfessionalProfileForm,
    WorkExperienceFormSet, EducationFormSet, SkillFormSet, 
    CertificationFormSet, ProjectFormSet, ReferenceFormSet
)


class CVDashboardView(TemplateView):
    """Main dashboard for CV management"""
    template_name = 'jobassistant/cv_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user profiles
        if self.request.user.is_authenticated:
            profiles = UserProfile.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if session_key:
                profiles = UserProfile.objects.filter(session_key=session_key)
            else:
                profiles = UserProfile.objects.none()
        
        context['profiles'] = profiles
        return context


class CVBuilderView(TemplateView):
    """Professional multi-section CV builder"""
    template_name = 'jobassistant/cv_builder.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile_id = kwargs.get('profile_id')
        if profile_id:
            profile = get_object_or_404(UserProfile, id=profile_id)
        else:
            profile = None
        
        # Initialize all forms
        context.update({
            'profile': profile,
            'personal_form': PersonalInfoForm(instance=profile),
            'professional_form': ProfessionalProfileForm(instance=profile),
            'work_formset': WorkExperienceFormSet(instance=profile),
            'education_formset': EducationFormSet(instance=profile),
            'skill_formset': SkillFormSet(instance=profile),
            'certification_formset': CertificationFormSet(instance=profile),
            'project_formset': ProjectFormSet(instance=profile),
            'reference_formset': ReferenceFormSet(instance=profile),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submissions for all sections"""
        profile_id = kwargs.get('profile_id')
        
        if profile_id:
            profile = get_object_or_404(UserProfile, id=profile_id)
        else:
            # Create new profile
            profile = UserProfile()
            if request.user.is_authenticated:
                profile.user = request.user
            else:
                if not request.session.session_key:
                    request.session.create()
                profile.session_key = request.session.session_key
        
        # Get section being submitted
        section = request.POST.get('section', 'personal')
        
        with transaction.atomic():
            success = False
            
            if section == 'personal':
                success = self._handle_personal_section(request, profile)
            elif section == 'professional':
                success = self._handle_professional_section(request, profile)
            elif section == 'work_experience':
                success = self._handle_work_experience_section(request, profile)
            elif section == 'education':
                success = self._handle_education_section(request, profile)
            elif section == 'skills':
                success = self._handle_skills_section(request, profile)
            elif section == 'certifications':
                success = self._handle_certifications_section(request, profile)
            elif section == 'projects':
                success = self._handle_projects_section(request, profile)
            elif section == 'references':
                success = self._handle_references_section(request, profile)
            
            if success:
                messages.success(request, f'{section.replace("_", " ").title()} section updated successfully!')
                return redirect('jobassistant:cv_builder', profile_id=profile.id)
        
        # If we get here, there were errors
        messages.error(request, 'Please correct the errors below.')
        return self.get(request, *args, **kwargs)
    
    def _handle_personal_section(self, request, profile):
        """Handle personal information form"""
        form = PersonalInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return True
        return False
    
    def _handle_professional_section(self, request, profile):
        """Handle professional profile form"""
        form = ProfessionalProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return True
        return False
    
    def _handle_work_experience_section(self, request, profile):
        """Handle work experience formset"""
        formset = WorkExperienceFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False
    
    def _handle_education_section(self, request, profile):
        """Handle education formset"""
        formset = EducationFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False
    
    def _handle_skills_section(self, request, profile):
        """Handle skills formset"""
        formset = SkillFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False
    
    def _handle_certifications_section(self, request, profile):
        """Handle certifications formset"""
        formset = CertificationFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False
    
    def _handle_projects_section(self, request, profile):
        """Handle projects formset"""
        formset = ProjectFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False
    
    def _handle_references_section(self, request, profile):
        """Handle references formset"""
        formset = ReferenceFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return True
        return False


class CVPreviewView(TemplateView):
    """Preview CV in different formats"""
    template_name = 'jobassistant/cv_preview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = kwargs.get('profile_id')
        profile = get_object_or_404(UserProfile, id=profile_id)
        
        context['profile'] = profile
        return context


def create_new_cv(request):
    """Create a new CV profile"""
    profile = UserProfile()
    
    if request.user.is_authenticated:
        profile.user = request.user
    else:
        if not request.session.session_key:
            request.session.create()
        profile.session_key = request.session.session_key
    
    # Set default values
    profile.first_name = ""
    profile.last_name = ""
    profile.email = ""
    profile.mobile_phone = ""
    profile.address_line_1 = ""
    profile.city = ""
    profile.state_region = ""
    profile.country = "New Zealand"
    profile.postal_code = ""
    profile.professional_summary = ""
    
    profile.save()
    
    messages.success(request, 'New CV started! Please fill in your details.')
    return redirect('jobassistant:cv_builder', profile_id=profile.id)


def delete_cv(request, profile_id):
    """Delete a CV profile"""
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    # Check ownership
    if request.user.is_authenticated:
        if profile.user != request.user:
            messages.error(request, 'You can only delete your own CVs.')
            return redirect('jobassistant:cv_dashboard')
    else:
        if profile.session_key != request.session.session_key:
            messages.error(request, 'You can only delete your own CVs.')
            return redirect('jobassistant:cv_dashboard')
    
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'CV deleted successfully.')
        return redirect('jobassistant:cv_dashboard')
    
    return render(request, 'jobassistant/cv_delete_confirm.html', {'profile': profile})


# AJAX views for dynamic sections
def add_work_experience(request):
    """Add work experience entry via AJAX"""
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        profile = get_object_or_404(UserProfile, id=profile_id)
        
        formset = WorkExperienceFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': formset.errors})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def auto_save_section(request):
    """Auto-save section data via AJAX"""
    if request.method == 'POST':
        try:
            profile_id = request.POST.get('profile_id')
            section = request.POST.get('section')
            
            profile = get_object_or_404(UserProfile, id=profile_id)
            
            # Handle different sections
            if section == 'personal':
                form = PersonalInfoForm(request.POST, instance=profile)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Personal info auto-saved'})
            
            elif section == 'professional':
                form = ProfessionalProfileForm(request.POST, instance=profile)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Professional profile auto-saved'})
            
            return JsonResponse({'success': False, 'error': 'Validation failed'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def calculate_completion(request, profile_id):
    """Calculate CV completion percentage"""
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    # Calculate completion based on filled fields
    total_sections = 8
    completed_sections = 0
    
    # Personal info (required fields)
    if (profile.first_name and profile.last_name and profile.email and 
        profile.mobile_phone and profile.city):
        completed_sections += 1
    
    # Professional profile
    if profile.professional_summary:
        completed_sections += 1
    
    # Work experience
    if profile.work_experiences.exists():
        completed_sections += 1
    
    # Education
    if profile.education_entries.exists():
        completed_sections += 1
    
    # Skills
    if profile.skills.exists():
        completed_sections += 1
    
    # At least one additional section
    if (profile.certifications.exists() or profile.projects.exists() or 
        profile.awards.exists() or profile.memberships.exists() or 
        profile.volunteer_work.exists()):
        completed_sections += 1
    
    # References
    if profile.references.exists():
        completed_sections += 1
    
    # Contact details complete
    if (profile.address_line_1 and profile.state_region and 
        profile.country and profile.postal_code):
        completed_sections += 1
    
    percentage = int((completed_sections / total_sections) * 100)
    
    # Update profile
    profile.profile_completion_percentage = percentage
    profile.save()
    
    return JsonResponse({
        'percentage': percentage,
        'completed_sections': completed_sections,
        'total_sections': total_sections
    })


# Legacy views to maintain compatibility
def dashboard(request):
    """Redirect to new CV dashboard"""
    return redirect('jobassistant:cv_dashboard')


def profile_manual(request):
    """Redirect to CV builder"""
    return redirect('jobassistant:create_cv')
