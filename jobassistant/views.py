from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import TemplateView

# Temporary minimal views for migration
class HomeView(TemplateView):
    """Temporary home view"""
    template_name = 'jobassistant/coming_soon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Professional CV Builder - Coming Soon',
            'message': 'The new professional CV builder is being deployed. Please check back soon!'
        })
        return context

def dashboard(request):
    """Temporary dashboard view"""
    return render(request, 'jobassistant/coming_soon.html', {
        'title': 'Professional CV Builder - Coming Soon',
        'message': 'The new professional CV builder is being deployed. Please check back soon!'
    })

def about(request):
    """Temporary about view"""
    return render(request, 'jobassistant/coming_soon.html', {
        'title': 'About - Coming Soon',
        'message': 'Learn more about our professional CV builder. Check back soon!'
    })

def scrape_job_url(request):
    """Temporary scrape job view"""
    messages.info(request, 'Job scraping feature will be available soon.')
    return redirect('jobassistant:home')

def job_details(request, job_id):
    """Temporary job details view"""
    messages.info(request, 'Job details feature will be available soon.')
    return redirect('jobassistant:home')

def upload_resume(request):
    """Temporary upload resume view"""
    messages.info(request, 'Resume upload feature will be available soon.')
    return redirect('jobassistant:home')

def profile_review(request, profile_id):
    """Temporary profile review view"""
    messages.info(request, 'Profile review feature will be available soon.')
    return redirect('jobassistant:home')

def manual_profile_entry(request):
    """Temporary manual profile entry view"""
    messages.info(request, 'Manual profile entry feature will be available soon.')
    return redirect('jobassistant:home')

def document_options(request):
    """Temporary document options view"""
    messages.info(request, 'Document options feature will be available soon.')
    return redirect('jobassistant:home')

def generate_documents(request):
    """Temporary generate documents view"""
    messages.info(request, 'Document generation feature will be available soon.')
    return redirect('jobassistant:home')

def download_documents(request):
    """Temporary download documents view"""
    messages.info(request, 'Document download feature will be available soon.')
    return redirect('jobassistant:home')

def download_file(request, doc_id, file_type):
    """Temporary download file view"""
    messages.info(request, 'File download feature will be available soon.')
    return redirect('jobassistant:home')

def toggle_version(request):
    """Temporary toggle version view"""
    messages.info(request, 'Version toggle feature will be available soon.')
    return redirect('jobassistant:home')

def settings_view(request):
    """Temporary settings view"""
    messages.info(request, 'Settings feature will be available soon.')
    return redirect('jobassistant:home')

def clear_session(request):
    """Temporary clear session view"""
    messages.info(request, 'Session clearing feature will be available soon.')
    return redirect('jobassistant:home')

def check_scraping_status(request, session_id):
    """Temporary scraping status API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Scraping status API will be available soon.'})

def get_progress(request, task_id):
    """Temporary progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Progress API will be available soon.'})

def debug_progress(request):
    """Temporary debug progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Debug progress API will be available soon.'})

def create_test_progress(request):
    """Temporary create test progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Test progress API will be available soon.'})

def recover_progress(request, task_id):
    """Temporary recover progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Recover progress API will be available soon.'})

def scrape_job_with_progress(request):
    """Temporary scrape job with progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Scrape job with progress API will be available soon.'})

def parse_resume_with_progress(request):
    """Temporary parse resume with progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Parse resume with progress API will be available soon.'})

def generate_documents_with_progress(request):
    """Temporary generate documents with progress API"""
    return JsonResponse({'status': 'coming_soon', 'message': 'Generate documents with progress API will be available soon.'})

def progress_test_page(request):
    """Temporary progress test page"""
    messages.info(request, 'Progress test page will be available soon.')
    return redirect('jobassistant:home')

def profile_manual(request):
    """Temporary profile view"""
    return redirect('jobassistant:dashboard')

def cv_dashboard(request):
    """Temporary CV dashboard"""
    return redirect('jobassistant:dashboard')
