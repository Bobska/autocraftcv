from django import forms
from django.forms import inlineformset_factory
from .models import (
    UserProfile, WorkExperience, Education, Skill, Certification,
    Project, Award, ProfessionalMembership, VolunteerWork, Publication, Reference
)


class PersonalInfoForm(forms.ModelForm):
    """Form for personal information section"""
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'mobile_phone', 'landline_phone',
            'address_line_1', 'address_line_2', 'city', 'state_region', 'country',
            'postal_code', 'linkedin_url', 'portfolio_url', 'github_url'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'your.email@example.com'
            }),
            'mobile_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+64 21 123 4567'
            }),
            'landline_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+64 9 123 4567 (optional)'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main Street'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auckland'
            }),
            'state_region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auckland Region'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('New Zealand', 'New Zealand'),
                ('Australia', 'Australia'),
                ('Other', 'Other')
            ]),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1010'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
        }


class ProfessionalProfileForm(forms.ModelForm):
    """Form for professional profile section"""
    
    class Meta:
        model = UserProfile
        fields = [
            'professional_summary', 'career_objectives', 'value_proposition',
            'target_industry', 'years_experience', 'employment_status',
            'visa_work_rights', 'availability', 'drivers_license', 'willing_to_relocate'
        ]
        
        widgets = {
            'professional_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write 2-3 sentences highlighting your key strengths, experience, and career goals...'
            }),
            'career_objectives': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your career goals and aspirations...'
            }),
            'value_proposition': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What unique value do you bring to employers?...'
            }),
            'target_industry': forms.Select(attrs={
                'class': 'form-select'
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visa_work_rights': forms.Select(attrs={
                'class': 'form-select'
            }),
            'availability': forms.Select(attrs={
                'class': 'form-select'
            }),
            'drivers_license': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'willing_to_relocate': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class WorkExperienceForm(forms.ModelForm):
    """Form for individual work experience entries"""
    
    class Meta:
        model = WorkExperience
        fields = [
            'job_title', 'company_name', 'company_location', 'employment_type',
            'start_date', 'end_date', 'currently_working', 'key_responsibilities',
            'key_achievements', 'skills_used', 'reason_for_leaving'
        ]
        
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tech Company Ltd'
            }),
            'company_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Auckland, New Zealand'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'currently_working': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'key_responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '• Responsibility 1\n• Responsibility 2\n• Responsibility 3'
            }),
            'key_achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '• Achievement 1\n• Achievement 2\n• Achievement 3'
            }),
            'skills_used': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, JavaScript, Project Management'
            }),
            'reason_for_leaving': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Career advancement, relocation, etc.'
            }),
        }


class EducationForm(forms.ModelForm):
    """Form for individual education entries"""
    
    class Meta:
        model = Education
        fields = [
            'degree_type', 'field_of_study', 'institution_name', 'institution_location',
            'graduation_year', 'gpa_grade', 'relevant_coursework', 'academic_achievements',
            'thesis_project_title'
        ]
        
        widgets = {
            'degree_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science, Business Administration'
            }),
            'institution_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., University of Auckland'
            }),
            'institution_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Auckland, New Zealand'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1950,
                'max': 2030
            }),
            'gpa_grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3.8/4.0, First Class Honours, A+'
            }),
            'relevant_coursework': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List relevant courses, projects, or specializations...'
            }),
            'academic_achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dean\'s List, scholarships, awards...'
            }),
            'thesis_project_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title of your thesis or final project'
            }),
        }


class SkillForm(forms.ModelForm):
    """Form for individual skills"""
    
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency_level', 'years_experience']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python, Leadership, Microsoft Excel'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'proficiency_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'placeholder': 'Years'
            }),
        }


class CertificationForm(forms.ModelForm):
    """Form for individual certifications"""
    
    class Meta:
        model = Certification
        fields = [
            'name', 'issuing_organization', 'issue_date', 'expiration_date',
            'certification_number', 'verification_url', 'still_valid'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., AWS Certified Solutions Architect'
            }),
            'issuing_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Amazon Web Services'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certification_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Certificate ID or number'
            }),
            'verification_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://verify.example.com/certificate'
            }),
            'still_valid': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProjectForm(forms.ModelForm):
    """Form for individual projects"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'project_type', 'description', 'role_responsibilities',
            'technologies_used', 'start_date', 'end_date', 'project_url',
            'github_url', 'results_outcomes'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., E-commerce Platform'
            }),
            'project_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the project...'
            }),
            'role_responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your role and key responsibilities...'
            }),
            'technologies_used': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, React, PostgreSQL'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'project_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://project.example.com'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/user/project'
            }),
            'results_outcomes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Results, metrics, impact of the project...'
            }),
        }


class ReferenceForm(forms.ModelForm):
    """Form for individual references"""
    
    class Meta:
        model = Reference
        fields = [
            'name', 'job_title', 'company_organization', 'phone', 'email',
            'relationship', 'relationship_description'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., John Smith'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Manager'
            }),
            'company_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., ABC Company Ltd'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+64 21 123 4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john.smith@company.com'
            }),
            'relationship': forms.Select(attrs={
                'class': 'form-select'
            }),
            'relationship_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Direct supervisor for 2 years'
            }),
        }


# Create formsets for dynamic sections
WorkExperienceFormSet = inlineformset_factory(
    UserProfile, WorkExperience,
    form=WorkExperienceForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

EducationFormSet = inlineformset_factory(
    UserProfile, Education,
    form=EducationForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

SkillFormSet = inlineformset_factory(
    UserProfile, Skill,
    form=SkillForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

CertificationFormSet = inlineformset_factory(
    UserProfile, Certification,
    form=CertificationForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

ProjectFormSet = inlineformset_factory(
    UserProfile, Project,
    form=ProjectForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

ReferenceFormSet = inlineformset_factory(
    UserProfile, Reference,
    form=ReferenceForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)


# Additional quick forms for dynamic sections
class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = ['name', 'issuing_organization', 'date_received', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control'}),
            'date_received': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ProfessionalMembershipForm(forms.ModelForm):
    class Meta:
        model = ProfessionalMembership
        fields = ['organization_name', 'membership_type', 'start_date', 'end_date', 'currently_active']
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'membership_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'currently_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VolunteerWorkForm(forms.ModelForm):
    class Meta:
        model = VolunteerWork
        fields = ['organization_name', 'role_title', 'start_date', 'end_date', 'currently_active', 'key_activities', 'skills_gained']
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role_title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'currently_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'key_activities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills_gained': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'publication_name', 'publication_date', 'co_authors', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'co_authors': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Create additional formsets
AwardFormSet = inlineformset_factory(
    UserProfile, Award, form=AwardForm, extra=1, can_delete=True
)

ProfessionalMembershipFormSet = inlineformset_factory(
    UserProfile, ProfessionalMembership, form=ProfessionalMembershipForm, extra=1, can_delete=True
)

VolunteerWorkFormSet = inlineformset_factory(
    UserProfile, VolunteerWork, form=VolunteerWorkForm, extra=1, can_delete=True
)

PublicationFormSet = inlineformset_factory(
    UserProfile, Publication, form=PublicationForm, extra=1, can_delete=True
)


# Temporary placeholder forms for compatibility
class ManualJobEntryForm(forms.Form):
    """Temporary placeholder"""
    pass

class SmartManualEntryForm(forms.Form):
    """Temporary placeholder"""
    pass

class LinkedInCredentialsForm(forms.Form):
    """Temporary placeholder"""
    pass

class JobURLForm(forms.Form):
    """Temporary placeholder"""
    pass

class ResumeUploadForm(forms.Form):
    """Temporary placeholder"""
    pass


class ComprehensiveCVForm(forms.ModelForm):
    """Comprehensive form for editing all UserProfile fields in CV edit view"""
    
    class Meta:
        model = UserProfile
        fields = [
            # Personal Information
            'first_name', 'last_name', 'email', 'mobile_phone', 'landline_phone',
            'address_line_1', 'address_line_2', 'city', 'state_region', 'country',
            'postal_code', 'linkedin_url', 'portfolio_url', 'github_url',
            
            # Professional Profile  
            'professional_summary', 'career_objectives', 'value_proposition',
            'target_industry', 'years_experience', 'employment_status',
            'visa_work_rights', 'availability', 'drivers_license', 'willing_to_relocate'
        ]
        
        widgets = {
            # Personal Information widgets
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'your.email@example.com'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '+64 21 123 4567'}),
            'landline_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+64 9 123 4567 (optional)'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main Street'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, etc. (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auckland'}),
            'state_region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auckland Region'}),
            'country': forms.Select(attrs={'class': 'form-select'}, choices=[('New Zealand', 'New Zealand'), ('Australia', 'Australia'), ('Other', 'Other')]),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1010'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/yourusername'}),
            
            # Professional Profile widgets
            'professional_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write 2-3 sentences highlighting your key strengths, experience, and career goals...'}),
            'career_objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your career goals and aspirations...'}),
            'value_proposition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What unique value do you bring to employers?...'}),
            'target_industry': forms.Select(attrs={'class': 'form-select'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'visa_work_rights': forms.Select(attrs={'class': 'form-select'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'drivers_license': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SkillsForm(forms.Form):
    """Form for skills section in CV wizard"""
    
    technical_skills = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Python, JavaScript, React, AWS, SQL, Git, etc. (separate with commas)'
        }),
        help_text='List your technical skills separated by commas'
    )
    
    soft_skills = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Leadership, Communication, Problem-solving, Team management, etc. (separate with commas)'
        }),
        help_text='List your soft skills separated by commas'
    )
    
    def __init__(self, *args, **kwargs):
        # Extract user_profile if provided
        user_profile = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # Pre-populate with existing skills
            technical_skills = user_profile.skills.filter(category='technical').values_list('name', flat=True)
            soft_skills = user_profile.skills.filter(category='soft').values_list('name', flat=True)
            
            if technical_skills:
                self.fields['technical_skills'].initial = ', '.join(technical_skills)
            if soft_skills:
                self.fields['soft_skills'].initial = ', '.join(soft_skills)


class WorkExperienceWizardForm(forms.Form):
    """Simplified form for work experience in CV wizard"""
    
    job_title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Senior Software Engineer'
        })
    )
    
    company_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Tech Solutions Ltd'
        })
    )
    
    company_location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Auckland, New Zealand'
        })
    )
    
    employment_type = forms.ChoiceField(
        choices=[('', 'Select employment type')] + WorkExperience.EMPLOYMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    currently_working = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    key_responsibilities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '• Responsibility 1\n• Responsibility 2\n• Responsibility 3'
        })
    )
    
    key_achievements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '• Achievement 1\n• Achievement 2\n• Achievement 3'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # Pre-populate with the most recent work experience
            latest_work = user_profile.work_experiences.first()
            if latest_work:
                self.fields['job_title'].initial = latest_work.job_title
                self.fields['company_name'].initial = latest_work.company_name
                self.fields['company_location'].initial = latest_work.company_location
                self.fields['employment_type'].initial = latest_work.employment_type
                self.fields['start_date'].initial = latest_work.start_date
                self.fields['end_date'].initial = latest_work.end_date
                self.fields['currently_working'].initial = latest_work.currently_working
                self.fields['key_responsibilities'].initial = latest_work.key_responsibilities
                self.fields['key_achievements'].initial = latest_work.key_achievements


class EducationWizardForm(forms.Form):
    """Simplified form for education in CV wizard"""
    
    degree_type = forms.ChoiceField(
        choices=[('', 'Select degree type')] + Education.DEGREE_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    field_of_study = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Computer Science, Business Administration'
        })
    )
    
    institution_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., University of Auckland'
        })
    )
    
    institution_location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Auckland, New Zealand'
        })
    )
    
    graduation_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1950,
            'max': 2030,
            'placeholder': 'e.g., 2023'
        })
    )
    
    gpa_grade = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 3.8 GPA, A-, Distinction'
        })
    )
    
    relevant_coursework = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List relevant courses, projects, or specializations...'
        })
    )
    
    academic_achievements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dean\'s List, scholarships, academic awards...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # Pre-populate with the most recent education
            latest_education = user_profile.education_entries.first()
            if latest_education:
                self.fields['degree_type'].initial = latest_education.degree_type
                self.fields['field_of_study'].initial = latest_education.field_of_study
                self.fields['institution_name'].initial = latest_education.institution_name
                self.fields['institution_location'].initial = latest_education.institution_location
                self.fields['graduation_year'].initial = latest_education.graduation_year
                self.fields['gpa_grade'].initial = latest_education.gpa_grade
                self.fields['relevant_coursework'].initial = latest_education.relevant_coursework
                self.fields['academic_achievements'].initial = latest_education.academic_achievements
