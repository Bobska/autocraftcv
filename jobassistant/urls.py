from django.urls import path
from . import views

app_name = 'jobassistant'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    
    # Job processing
    path('scrape-job/', views.scrape_job_url, name='scrape_job_url'),
    path('job/<uuid:job_id>/', views.job_details, name='job_details'),
    
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
]
