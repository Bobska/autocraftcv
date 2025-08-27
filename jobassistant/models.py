from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os


class JobPosting(models.Model):
    """Model to store job posting information scraped from URLs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=200, blank=True, null=True)  # Allow null values
    company = models.CharField(max_length=200, blank=True, null=True)  # Allow null values
    location = models.CharField(max_length=200, blank=True, null=True)  # Allow null values - FIX for constraint error
    description = models.TextField(blank=True, null=True)  # Allow null values
    requirements = models.TextField(blank=True, null=True)  # Allow null values
    qualifications = models.TextField(blank=True, null=True)  # Allow null values
    responsibilities = models.TextField(blank=True, null=True)  # Allow null values
    salary_range = models.CharField(max_length=100, blank=True, null=True)  # Allow null values
    employment_type = models.CharField(max_length=50, blank=True, null=True)  # Allow null values
    application_instructions = models.TextField(blank=True, null=True)  # Allow null values
    
    # Metadata
    scraped_at = models.DateTimeField(default=timezone.now)
    raw_content = models.TextField(blank=True, null=True)  # Allow null values
    scraping_method = models.CharField(max_length=50, default='beautifulsoup')  # beautifulsoup, selenium, api
    extraction_method = models.CharField(max_length=100, blank=True, null=True)  # Allow null values
    site_domain = models.CharField(max_length=100, blank=True, null=True)  # Allow null values
    needs_review = models.BooleanField(default=False)  # Manual review required
    
    class Meta:
        ordering = ['-scraped_at']
    
    def __str__(self):
        title = self.title or 'No Title'
        company = self.company or 'Unknown Company'
        return f"{title} at {company}"


class UserProfile(models.Model):
    """Model to store user resume/profile information"""
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior Level (6-10 years)'),
        ('lead', 'Lead/Principal (10+ years)'),
        ('executive', 'Executive/C-Level'),
    ]
    
    VISA_STATUS_CHOICES = [
        ('nz_citizen', 'New Zealand Citizen'),
        ('au_citizen', 'Australian Citizen'),
        ('au_pr', 'Australian Permanent Resident'),
        ('nz_resident', 'New Zealand Resident'),
        ('open_work_visa', 'Open Work Visa'),
        ('employer_sponsored', 'Employer Sponsored Visa'),
        ('student_visa', 'Student Visa'),
        ('working_holiday', 'Working Holiday Visa'),
        ('other', 'Other (specify in notes)'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('immediate', 'Immediate'),
        ('1_week', '1 Week'),
        ('2_weeks', '2 Weeks'),
        ('1_month', '1 Month'),
        ('negotiable', 'Negotiable'),
    ]
    
    REFERENCES_CHOICE = [
        ('provided', 'References Provided'),
        ('on_request', 'Available on Request'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users
    
    # 1. Personal Details (Required and Optional)
    full_name = models.CharField(max_length=200)  # Required
    email = models.EmailField()  # Required
    phone = models.CharField(max_length=20)  # Required
    city_region = models.CharField(max_length=100, blank=True)  # Required (City & Region)
    job_title = models.CharField(max_length=150, blank=True)  # Optional (Job Title/Profession)
    linkedin_url = models.URLField(blank=True)  # Optional
    portfolio_url = models.URLField(blank=True)  # Optional
    github_url = models.URLField(blank=True)  # Optional
    photo = models.ImageField(upload_to='cv_photos/', blank=True, null=True)  # Optional (not recommended)
    
    # 2. Professional Summary / Career Objective (Required)
    professional_summary = models.TextField(help_text="2-4 sentences highlighting your key strengths and career goals")  # Required
    
    # 3. Key Skills (Required: at least 5 skills)
    technical_skills = models.TextField(blank=True, help_text="Technical skills separated by commas")
    soft_skills = models.TextField(blank=True, help_text="Soft skills separated by commas")
    
    # Legacy field for backward compatibility
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    
    # 4. Work Experience (Required: at least 1 entry) - stored as JSON for structured data
    work_experience = models.TextField(blank=True, help_text="JSON formatted work experience entries")
    
    # 5. Education (Required: at least highest qualification) - stored as JSON
    education = models.TextField(blank=True, help_text="JSON formatted education entries")
    
    # 6. Certifications / Licences (Optional) - stored as JSON
    certifications = models.TextField(blank=True, help_text="JSON formatted certifications")
    
    # 7. Projects / Portfolio (Optional) - stored as JSON
    projects = models.TextField(blank=True, help_text="JSON formatted project entries")
    
    # 8. Achievements / Awards (Optional) - stored as JSON
    achievements = models.TextField(blank=True, help_text="JSON formatted achievements")
    
    # 9. Volunteer / Community Work (Optional) - stored as JSON
    volunteer_work = models.TextField(blank=True, help_text="JSON formatted volunteer work")
    
    # 10. Professional Memberships (Optional) - stored as JSON
    professional_memberships = models.TextField(blank=True, help_text="JSON formatted memberships")
    
    # 11. References (Required choice)
    references_choice = models.CharField(max_length=20, choices=REFERENCES_CHOICE, default='on_request')
    references = models.TextField(blank=True, help_text="JSON formatted referee details")
    
    # 12. Extras (NZ/AU-specific, Optional)
    visa_work_rights = models.CharField(max_length=30, choices=VISA_STATUS_CHOICES, blank=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, blank=True)
    drivers_license = models.BooleanField(default=False)
    
    # Additional fields
    languages = models.TextField(blank=True, help_text="Languages and proficiency levels")
    
    # File uploads
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    parsed_content = models.TextField(blank=True)  # Parsed resume content
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_skills_list(self):
        """Return technical skills as a list"""
        if self.technical_skills:
            return [skill.strip() for skill in self.technical_skills.split(',') if skill.strip()]
        return []
    
    def get_soft_skills_list(self):
        """Return soft skills as a list"""
        if self.soft_skills:
            return [skill.strip() for skill in self.soft_skills.split(',') if skill.strip()]
        return []


class GeneratedDocument(models.Model):
    """Model to store generated cover letters and resumes"""
    
    DOCUMENT_TYPES = [
        ('cover_letter', 'Cover Letter'),
        ('resume', 'Tailored Resume'),
    ]
    
    GENERATION_METHODS = [
        ('template', 'Template-based'),
        ('huggingface', 'Hugging Face Model'),
        ('ollama', 'Ollama Local Model'),
        ('openai', 'OpenAI GPT'),
        ('anthropic', 'Anthropic Claude'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    generation_method = models.CharField(max_length=20, choices=GENERATION_METHODS)
    
    # Content
    content = models.TextField()
    title = models.CharField(max_length=200, blank=True)
    
    # Generated files
    pdf_file = models.FileField(upload_to='generated/pdf/', blank=True, null=True)
    docx_file = models.FileField(upload_to='generated/docx/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    generation_time = models.FloatField(null=True, blank=True)  # Time taken to generate in seconds
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document_type} for {self.job_posting.title} ({self.user_profile.full_name})"
    
    def delete(self, *args, **kwargs):
        """Delete associated files when model instance is deleted"""
        if self.pdf_file:
            if os.path.isfile(self.pdf_file.path):
                os.remove(self.pdf_file.path)
        if self.docx_file:
            if os.path.isfile(self.docx_file.path):
                os.remove(self.docx_file.path)
        super().delete(*args, **kwargs)


class ScrapingSession(models.Model):
    """Model to track scraping sessions and results"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    method_used = models.CharField(max_length=50, blank=True)
    
    # Results
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Scraping {self.url} - {self.status}"


class AppSettings(models.Model):
    """Model to store application settings and configurations"""
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=''):
        """Set a setting value"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            setting.value = value
            setting.description = description
            setting.save()
        return setting


class ProgressTask(models.Model):
    """Model to store progress tracking data for long-running tasks"""
    
    TASK_TYPES = [
        ('job_scraping', 'Job Scraping'),
        ('resume_parsing', 'Resume Parsing'),
        ('document_generation', 'Document Generation'),
        ('other', 'Other'),
    ]
    
    TASK_STATUS = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    task_id = models.CharField(max_length=100, primary_key=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES, default='other')
    status = models.CharField(max_length=50, choices=TASK_STATUS, default='running')
    progress = models.IntegerField(default=0)  # 0-100
    stage = models.CharField(max_length=20, default='0/0')
    status_message = models.CharField(max_length=500, default='Initializing...')
    error_message = models.TextField(blank=True, null=True)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Additional data as JSON
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task_id} - {self.get_task_type_display()} ({self.progress}%)"
    
    def mark_completed(self, status_message="Complete!"):
        """Mark the task as completed"""
        self.status = 'completed'
        self.progress = 100
        self.status_message = status_message
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark the task as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()
    
    def update_progress(self, progress, status_message, stage=None):
        """Update task progress"""
        self.progress = min(progress, 100)
        self.status_message = status_message
        if stage:
            self.stage = stage
        self.save()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'task_id': self.task_id,
            'progress': self.progress,
            'status': self.status_message,
            'stage': self.stage,
            'error': self.error_message,
            'completed': self.status in ['completed', 'failed', 'timeout'],
            'elapsed_time': int((timezone.now() - self.created_at).total_seconds()),
            'timestamp': self.updated_at.timestamp(),
            **self.additional_data
        }
