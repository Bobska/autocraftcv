from django.contrib import admin
from .models import (
    JobPosting, UserProfile, ProgressTask,
    WorkExperience, Education, Skill, Certification,
    Project, Award, ProfessionalMembership, VolunteerWork,
    Publication, Reference
)


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
            'fields': ('scraped_at', 'scraping_method', 'extraction_method', 'site_domain', 'needs_review')
        }),
        ('Raw Data', {
            'fields': ('raw_content',),
            'classes': ('collapse',)
        })
    )


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0
    fields = ('job_title', 'company_name', 'start_date', 'end_date', 'currently_working')


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ('degree_type', 'field_of_study', 'institution_name', 'graduation_year')


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    fields = ('name', 'category', 'proficiency_level')


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ('name', 'issuing_organization', 'issue_date', 'still_valid')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'target_industry', 'years_experience', 'created_at')
    list_filter = ('target_industry', 'employment_status', 'visa_work_rights', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at', 'profile_completion_percentage')
    ordering = ('-created_at',)
    
    inlines = [WorkExperienceInline, EducationInline, SkillInline, CertificationInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('first_name', 'last_name'),
                'email',
                ('mobile_phone', 'landline_phone'),
                'address_line_1',
                'address_line_2',
                ('city', 'state_region'),
                ('country', 'postal_code'),
                ('linkedin_url', 'portfolio_url', 'github_url')
            )
        }),
        ('Professional Profile', {
            'fields': (
                'professional_summary',
                'career_objectives',
                'value_proposition',
                ('target_industry', 'years_experience'),
                'employment_status'
            )
        }),
        ('AU/NZ Specific', {
            'fields': (
                'visa_work_rights',
                'availability',
                ('drivers_license', 'willing_to_relocate')
            )
        }),
        ('Metadata', {
            'fields': (
                'profile_completion_percentage',
                'sections_completed',
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        })
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company_name', 'profile', 'start_date', 'end_date', 'currently_working')
    list_filter = ('employment_type', 'currently_working', 'start_date')
    search_fields = ('job_title', 'company_name', 'profile__first_name', 'profile__last_name')
    ordering = ('-start_date',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree_type', 'field_of_study', 'institution_name', 'profile', 'graduation_year')
    list_filter = ('degree_type', 'graduation_year')
    search_fields = ('field_of_study', 'institution_name', 'profile__first_name', 'profile__last_name')
    ordering = ('-graduation_year',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency_level', 'profile')
    list_filter = ('category', 'proficiency_level')
    search_fields = ('name', 'profile__first_name', 'profile__last_name')
    ordering = ('category', 'name')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'profile', 'issue_date', 'still_valid')
    list_filter = ('still_valid', 'issue_date', 'issuing_organization')
    search_fields = ('name', 'issuing_organization', 'profile__first_name', 'profile__last_name')
    ordering = ('-issue_date',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_type', 'profile', 'start_date', 'end_date')
    list_filter = ('project_type', 'start_date')
    search_fields = ('name', 'description', 'profile__first_name', 'profile__last_name')
    ordering = ('-start_date',)


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'profile', 'date_received')
    list_filter = ('date_received', 'issuing_organization')
    search_fields = ('name', 'issuing_organization', 'profile__first_name', 'profile__last_name')
    ordering = ('-date_received',)


@admin.register(ProfessionalMembership)
class ProfessionalMembershipAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'membership_type', 'profile', 'start_date', 'currently_active')
    list_filter = ('membership_type', 'currently_active', 'start_date')
    search_fields = ('organization_name', 'profile__first_name', 'profile__last_name')
    ordering = ('-start_date',)


@admin.register(VolunteerWork)
class VolunteerWorkAdmin(admin.ModelAdmin):
    list_display = ('role_title', 'organization_name', 'profile', 'start_date', 'currently_active')
    list_filter = ('currently_active', 'start_date')
    search_fields = ('role_title', 'organization_name', 'profile__first_name', 'profile__last_name')
    ordering = ('-start_date',)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_name', 'profile', 'publication_date')
    list_filter = ('publication_date', 'publication_name')
    search_fields = ('title', 'publication_name', 'profile__first_name', 'profile__last_name')
    ordering = ('-publication_date',)


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_title', 'company_organization', 'profile', 'relationship')
    list_filter = ('relationship',)
    search_fields = ('name', 'job_title', 'company_organization', 'profile__first_name', 'profile__last_name')
    ordering = ('name',)


@admin.register(ProgressTask)
class ProgressTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'status', 'progress', 'current_step', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('task_id', 'current_step')
    readonly_fields = ('task_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
