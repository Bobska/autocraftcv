from django.contrib import admin
from .models import JobPosting, UserProfile, GeneratedDocument, ScrapingSession, AppSettings


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'scraped_at', 'scraping_method')
    list_filter = ('scraped_at', 'scraping_method', 'employment_type')
    search_fields = ('title', 'company', 'location', 'url')
    readonly_fields = ('id', 'scraped_at')
    ordering = ('-scraped_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('url', 'title', 'company', 'location', 'employment_type', 'salary_range')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'qualifications', 'responsibilities')
        }),
        ('Metadata', {
            'fields': ('id', 'scraped_at', 'scraping_method', 'raw_content'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'experience_level', 'created_at')
    list_filter = ('experience_level', 'created_at')
    search_fields = ('full_name', 'email', 'technical_skills')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'location', 'linkedin_url', 'portfolio_url')
        }),
        ('Professional Details', {
            'fields': ('professional_summary', 'experience_level', 'technical_skills', 'soft_skills', 'certifications')
        }),
        ('Experience & Education', {
            'fields': ('education', 'work_experience', 'achievements')
        }),
        ('Files', {
            'fields': ('resume_file', 'parsed_content'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'user', 'session_key', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'generation_method', 'user_profile', 'created_at', 'generation_time')
    list_filter = ('document_type', 'generation_method', 'created_at')
    search_fields = ('title', 'user_profile__full_name', 'job_posting__title')
    readonly_fields = ('id', 'created_at', 'generation_time')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document_type', 'generation_method')
        }),
        ('Related Objects', {
            'fields': ('user_profile', 'job_posting')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Files', {
            'fields': ('pdf_file', 'docx_file')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'generation_time'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ScrapingSession)
class ScrapingSessionAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'method_used', 'started_at', 'completed_at')
    list_filter = ('status', 'method_used', 'started_at')
    search_fields = ('url', 'error_message')
    readonly_fields = ('id', 'started_at', 'completed_at')
    ordering = ('-started_at',)
    
    fieldsets = (
        ('Session Information', {
            'fields': ('url', 'status', 'method_used')
        }),
        ('Results', {
            'fields': ('job_posting', 'error_message')
        }),
        ('Timing', {
            'fields': ('id', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'created_at', 'updated_at')
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('key',)
    
    def value_preview(self, obj):
        """Show truncated value for better display"""
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


# Admin site customization
admin.site.site_header = "AutoCraftCV Administration"
admin.site.site_title = "AutoCraftCV Admin"
admin.site.index_title = "Welcome to AutoCraftCV Administration"
