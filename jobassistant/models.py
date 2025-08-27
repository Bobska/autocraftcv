from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# Core UserProfile model for personal information
class UserProfile(models.Model):
    """Enhanced user profile for professional CV builder"""
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior Level (6-10 years)'),
        ('lead', 'Lead/Principal (10+ years)'),
        ('executive', 'Executive/C-Level'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Currently Employed'),
        ('unemployed', 'Currently Seeking'),
        ('student', 'Student'),
        ('freelancer', 'Freelancer/Consultant'),
        ('career_break', 'Career Break'),
    ]
    
    TARGET_INDUSTRIES = [
        ('technology', 'Technology & IT'),
        ('finance', 'Finance & Banking'),
        ('healthcare', 'Healthcare & Medical'),
        ('education', 'Education & Training'),
        ('retail', 'Retail & Sales'),
        ('construction', 'Construction & Engineering'),
        ('hospitality', 'Hospitality & Tourism'),
        ('marketing', 'Marketing & Communications'),
        ('legal', 'Legal Services'),
        ('government', 'Government & Public Service'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('non_profit', 'Non-Profit & NGO'),
        ('media', 'Media & Entertainment'),
        ('other', 'Other'),
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
    
    PROFILE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    # Primary Key and User Association
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users
    
    # Section 1: Personal Information
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    mobile_phone = models.CharField(max_length=20, default='')
    landline_phone = models.CharField(max_length=20, blank=True, default='')
    address_line_1 = models.CharField(max_length=200, default='')
    address_line_2 = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, default='')
    state_region = models.CharField(max_length=100, default='')
    country = models.CharField(max_length=100, default='New Zealand')
    postal_code = models.CharField(max_length=20, default='')
    linkedin_url = models.URLField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # Section 2: Professional Profile
    professional_summary = models.TextField(
        blank=True, default='',
        help_text="2-3 sentences highlighting your key strengths and career goals"
    )
    career_objectives = models.TextField(blank=True, default='')
    value_proposition = models.TextField(blank=True, default='')
    target_industry = models.CharField(max_length=50, choices=TARGET_INDUSTRIES, blank=True, default='')
    years_experience = models.PositiveIntegerField(default=0)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, default='')
    
    # AU/NZ Specific Information
    visa_work_rights = models.CharField(max_length=30, choices=VISA_STATUS_CHOICES, blank=True, default='')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, blank=True, default='')
    drivers_license = models.BooleanField(default=False)
    willing_to_relocate = models.BooleanField(default=False)
    
    # Legacy fields for backward compatibility
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    
    # File uploads
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    parsed_content = models.TextField(blank=True)
    
    # Completion tracking
    profile_completion_percentage = models.PositiveIntegerField(default=0)
    sections_completed = models.JSONField(default=dict, blank=True)
    profile_status = models.CharField(max_length=20, choices=PROFILE_STATUS_CHOICES, default='draft')
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state_region}",
            self.postal_code,
            self.country
        ]
        return ", ".join([part for part in parts if part])


class WorkExperience(models.Model):
    """Dynamic work experience entries"""
    
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('casual', 'Casual'),
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
        ('freelance', 'Freelance'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='work_experiences')
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_location = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    key_responsibilities = models.TextField()
    key_achievements = models.TextField(blank=True)
    skills_used = models.TextField(blank=True, help_text="Comma-separated skills")
    reason_for_leaving = models.CharField(max_length=200, blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class Education(models.Model):
    """Dynamic education entries"""
    
    DEGREE_TYPES = [
        ('high_school', 'High School Certificate'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate/PhD'),
        ('professional', 'Professional Qualification'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education_entries')
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    field_of_study = models.CharField(max_length=200)
    institution_name = models.CharField(max_length=200)
    institution_location = models.CharField(max_length=200)
    graduation_year = models.PositiveIntegerField()
    gpa_grade = models.CharField(max_length=20, blank=True)
    relevant_coursework = models.TextField(blank=True)
    academic_achievements = models.TextField(blank=True)
    thesis_project_title = models.CharField(max_length=300, blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-graduation_year', 'order']
    
    def __str__(self):
        return f"{self.degree_type} in {self.field_of_study} - {self.institution_name}"


class Skill(models.Model):
    """Skills with categories and proficiency levels"""
    
    SKILL_CATEGORIES = [
        ('technical', 'Technical/Hard Skills'),
        ('software', 'Software Proficiency'),
        ('programming', 'Programming Languages'),
        ('soft', 'Soft Skills'),
        ('language', 'Language Skills'),
        ('industry', 'Industry-Specific Skills'),
    ]
    
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
        ('native', 'Native'), # For languages
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
        unique_together = ['profile', 'name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class Certification(models.Model):
    """Professional certifications and licenses"""
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    certification_number = models.CharField(max_length=100, blank=True)
    verification_url = models.URLField(blank=True)
    still_valid = models.BooleanField(default=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-issue_date', 'order']
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"


class Project(models.Model):
    """Portfolio projects"""
    
    PROJECT_TYPES = [
        ('personal', 'Personal'),
        ('professional', 'Professional'),
        ('academic', 'Academic'),
        ('open_source', 'Open Source'),
        ('freelance', 'Freelance'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    description = models.TextField()
    role_responsibilities = models.TextField()
    technologies_used = models.TextField(help_text="Comma-separated technologies")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    results_outcomes = models.TextField(blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.name} ({self.project_type})"


class Award(models.Model):
    """Awards and recognition"""
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='awards')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    date_received = models.DateField()
    description = models.TextField(blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date_received', 'order']
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"


class ProfessionalMembership(models.Model):
    """Professional memberships and associations"""
    
    MEMBERSHIP_TYPES = [
        ('member', 'Member'),
        ('fellow', 'Fellow'),
        ('associate', 'Associate'),
        ('student', 'Student Member'),
        ('honorary', 'Honorary Member'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='memberships')
    organization_name = models.CharField(max_length=200)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_active = models.BooleanField(default=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.organization_name} ({self.membership_type})"


class VolunteerWork(models.Model):
    """Volunteer work and community involvement"""
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='volunteer_work')
    organization_name = models.CharField(max_length=200)
    role_title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_active = models.BooleanField(default=False)
    key_activities = models.TextField()
    skills_gained = models.TextField(blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.role_title} at {self.organization_name}"


class Publication(models.Model):
    """Publications and research"""
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=300)
    publication_name = models.CharField(max_length=200)
    publication_date = models.DateField()
    co_authors = models.CharField(max_length=500, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-publication_date', 'order']
    
    def __str__(self):
        return f"{self.title} - {self.publication_name}"


class Reference(models.Model):
    """Professional references"""
    
    RELATIONSHIP_TYPES = [
        ('supervisor', 'Direct Supervisor'),
        ('manager', 'Manager'),
        ('colleague', 'Colleague'),
        ('client', 'Client'),
        ('mentor', 'Mentor'),
        ('professor', 'Professor/Teacher'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    company_organization = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    relationship_description = models.CharField(max_length=200, blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.job_title}"


# Keep existing JobPosting model
class JobPosting(models.Model):
    """Model to store job posting information scraped from URLs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=50, blank=True, null=True)
    application_instructions = models.TextField(blank=True, null=True)
    
    # Metadata
    scraped_at = models.DateTimeField(default=timezone.now)
    raw_content = models.TextField(blank=True, null=True)
    scraping_method = models.CharField(max_length=50, default='beautifulsoup')
    extraction_method = models.CharField(max_length=100, blank=True, null=True)
    site_domain = models.CharField(max_length=100, blank=True, null=True)
    needs_review = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-scraped_at']
    
    def __str__(self):
        title = self.title or 'No Title'
        company = self.company or 'Unknown Company'
        return f"{title} at {company}"


class ProgressTask(models.Model):
    """Model to track progress of CV parsing and generation tasks"""
    task_id = models.CharField(max_length=36, primary_key=True)  # UUID as string
    status = models.CharField(max_length=20, default='pending')  # pending, processing, completed, failed
    progress = models.IntegerField(default=0)  # 0-100
    current_step = models.CharField(max_length=100, blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Task {self.task_id} - {self.status} ({self.progress}%)"
