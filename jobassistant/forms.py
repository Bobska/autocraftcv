from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import UserProfile, JobPosting
import re


class JobURLForm(forms.Form):
    """Form for entering job posting URL"""
    
    url = forms.URLField(
        label='Job Posting URL',
        max_length=2000,
        widget=forms.URLInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'https://example.com/job-posting',
            'required': True
        }),
        help_text='Enter the URL of the job posting you want to apply for'
    )
    
    def clean_url(self):
        url = self.cleaned_data['url']
        
        # Basic URL validation
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Please enter a valid URL")
        
        # Check for supported domains (you can expand this list)
        supported_patterns = [
            r'linkedin\.com',
            r'indeed\.com',
            r'glassdoor\.com',
            r'monster\.com',
            r'jobs\..*',
            r'careers\..*',
            r'.*\.jobs',
        ]
        
        if not any(re.search(pattern, url, re.IGNORECASE) for pattern in supported_patterns):
            # Allow all URLs but show a warning
            pass  # We'll handle unsupported sites gracefully
        
        return url


class ResumeUploadForm(forms.Form):
    """Form for uploading resume files"""
    
    resume_file = forms.FileField(
        label='Upload Resume',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx',
            'required': True
        }),
        help_text='Upload your resume in PDF or Word format (max 10MB)'
    )
    
    def clean_resume_file(self):
        file = self.cleaned_data['resume_file']
        
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError("Only PDF and Word documents are allowed")
        
        return file


class UserProfileForm(forms.ModelForm):
    """Form for manual profile entry"""
    
    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'email', 'phone', 'location',
            'linkedin_url', 'portfolio_url', 'professional_summary',
            'experience_level', 'technical_skills', 'soft_skills',
            'certifications', 'education', 'work_experience', 'achievements'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john.doe@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'San Francisco, CA'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/johndoe'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://johndoe.com'
            }),
            'professional_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief summary of your professional background and key achievements...'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
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
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Degree, Institution, Year\nMajor achievements or relevant coursework...'
            }),
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
        
        help_texts = {
            'technical_skills': 'Enter skills separated by commas (e.g., Python, JavaScript, AWS)',
            'soft_skills': 'Enter soft skills separated by commas (e.g., Leadership, Communication)',
            'work_experience': 'List your work experience with key responsibilities and achievements',
            'achievements': 'Highlight specific achievements, metrics, and notable projects',
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            # Basic email validation is handled by EmailField
            return email.lower()
        return email
    
    def clean_technical_skills(self):
        skills = self.cleaned_data['technical_skills']
        if skills:
            # Clean up the skills list
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            return ', '.join(skills_list)
        return skills
    
    def clean_soft_skills(self):
        skills = self.cleaned_data['soft_skills']
        if skills:
            # Clean up the skills list
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            return ', '.join(skills_list)
        return skills


class DocumentGenerationForm(forms.Form):
    """Form for document generation options"""
    
    DOCUMENT_CHOICES = [
        ('cover_letter', 'Cover Letter'),
        ('resume', 'Tailored Resume'),
        ('both', 'Both Cover Letter and Resume'),
    ]
    
    OUTPUT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('both', 'Both PDF and Word'),
    ]
    
    document_type = forms.ChoiceField(
        choices=DOCUMENT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='cover_letter',
        label='What would you like to generate?'
    )
    
    output_format = forms.ChoiceField(
        choices=OUTPUT_FORMAT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='pdf',
        label='Output format'
    )
    
    custom_instructions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any specific instructions or points you want to emphasize? (optional)'
        }),
        required=False,
        label='Custom Instructions (Optional)',
        help_text='Provide any specific requirements or points you want to highlight'
    )


class VersionToggleForm(forms.Form):
    """Form for switching between free and paid versions"""
    
    VERSION_CHOICES = [
        ('free', 'Free Version (Open Source Tools)'),
        ('paid', 'Paid Version (Premium APIs)'),
    ]
    
    version = forms.ChoiceField(
        choices=VERSION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='free',
        label='Choose Version'
    )


class SettingsForm(forms.Form):
    """Form for application settings"""
    
    # API Keys for paid version
    openai_api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'sk-...'
        }),
        required=False,
        label='OpenAI API Key',
        help_text='Required for GPT-based content generation'
    )
    
    anthropic_api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'sk-ant-...'
        }),
        required=False,
        label='Anthropic API Key',
        help_text='Required for Claude-based content generation'
    )
    
    scrapingbee_api_key = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        }),
        required=False,
        label='ScrapingBee API Key',
        help_text='For reliable web scraping'
    )
    
    # Generation preferences
    ai_model_preference = forms.ChoiceField(
        choices=[
            ('template', 'Template-based (Fastest)'),
            ('local', 'Local AI Model (Moderate)'),
            ('openai', 'OpenAI GPT (Best Quality)'),
            ('anthropic', 'Anthropic Claude (Best Quality)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='template',
        label='AI Model Preference'
    )
    
    auto_download = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        initial=True,
        label='Auto-download generated documents'
    )


class FeedbackForm(forms.Form):
    """Form for user feedback"""
    
    RATING_CHOICES = [
        (5, '⭐⭐⭐⭐⭐ Excellent'),
        (4, '⭐⭐⭐⭐ Good'),
        (3, '⭐⭐⭐ Average'),
        (2, '⭐⭐ Poor'),
        (1, '⭐ Very Poor'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='How would you rate the generated content?'
    )
    
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please share your thoughts on the quality and usefulness of the generated content...'
        }),
        required=False,
        label='Additional Feedback (Optional)'
    )
    
    suggestions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any suggestions for improvement?'
        }),
        required=False,
        label='Suggestions (Optional)'
    )
