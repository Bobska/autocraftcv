from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

# Temporary minimal views for migration
def dashboard(request):
    """Temporary dashboard view"""
    return render(request, 'jobassistant/coming_soon.html', {
        'title': 'Professional CV Builder - Coming Soon',
        'message': 'The new professional CV builder is being deployed. Please check back soon!'
    })

def profile_manual(request):
    """Temporary profile view"""
    return redirect('jobassistant:dashboard')

def cv_dashboard(request):
    """Temporary CV dashboard"""
    return redirect('jobassistant:dashboard')
