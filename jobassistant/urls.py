from django.urls import path
from . import views
from . import test_views
from . import manual_views

app_name = 'jobassistant'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    
    # Job processing
    path('scrape-job/', views.scrape_job_url, name='scrape_job_url'),
    path('job/<uuid:job_id>/', views.job_details, name='job_details'),
    
    # Enhanced scraping with anti-detection
    path('enhanced-scrape/', manual_views.enhanced_scrape_job, name='enhanced_scrape_job'),
    
    # Manual entry system
    path('manual-entry/', manual_views.manual_job_entry, name='manual_job_entry'),
    path('manual-entry/help/', manual_views.manual_entry_help, name='manual_entry_help'),
    path('retry-scraping/', manual_views.retry_scraping, name='retry_scraping'),
    
    # Enhanced Manual Entry - LinkedIn Login + Manual Entry Enhancement
    path('enhanced-manual-entry/', manual_views.enhanced_manual_job_entry, name='enhanced_manual_entry'),
    path('smart-manual-entry/', manual_views.smart_manual_entry, name='smart_manual_entry'),
    path('linkedin-login-setup/', manual_views.linkedin_login_setup, name='linkedin_login_setup'),
    path('enhanced-scraping-workflow/', manual_views.enhanced_scraping_workflow, name='enhanced_scraping_workflow'),
    
    # Profile processing
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('profile/<uuid:profile_id>/review/', views.profile_review, name='profile_review'),
    path('profile/manual/', views.manual_profile_entry, name='manual_profile_entry'),
    
    # Document generation
    path('document-options/', views.document_options, name='document_options'),
    path('generate/', views.generate_documents, name='generate_documents'),
    path('download/', views.download_documents, name='download_documents'),
    path('download/<uuid:doc_id>/<str:file_type>/', views.download_file, name='download_file'),
    
    # Settings and utilities
    path('toggle-version/', views.toggle_version, name='toggle_version'),
    path('settings/', views.settings_view, name='settings'),
    path('clear-session/', views.clear_session, name='clear_session'),
    
    # API endpoints
    path('api/scraping-status/<uuid:session_id>/', views.check_scraping_status, name='check_scraping_status'),
    
    # Progress tracking API endpoints
    path('api/progress/<str:task_id>/', views.get_progress, name='get_progress'),
    path('api/progress-debug/', views.debug_progress, name='debug_progress'),
    path('api/create-test-progress/', views.create_test_progress, name='create_test_progress'),
    path('api/recover-progress/<str:task_id>/', views.recover_progress, name='recover_progress'),
    path('api/scrape-with-progress/', views.scrape_job_with_progress, name='scrape_job_with_progress'),
    path('api/parse-resume-with-progress/', views.parse_resume_with_progress, name='parse_resume_with_progress'),
    path('api/generate-documents-with-progress/', views.generate_documents_with_progress, name='generate_documents_with_progress'),
    
    # Testing and debugging endpoints
    path('scraping-test/', test_views.test_scraping_page, name='test_scraping_page'),
    path('progress-test/', views.progress_test_page, name='progress_test_page'),
    path('api/test-scraping/', test_views.test_scraping, name='test_scraping'),
]
