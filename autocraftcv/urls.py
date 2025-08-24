"""
URL configuration for autocraftcv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from django.views.generic import RedirectView
import os

def favicon_view(request):
    """Serve favicon"""
    favicon_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'favicon.svg')
    if os.path.exists(favicon_path):
        return FileResponse(open(favicon_path, 'rb'), content_type='image/svg+xml')
    else:
        # Fallback to redirect
        return RedirectView.as_view(url='/static/images/favicon.svg', permanent=True)(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon_view, name='favicon'),
    path('', include('jobassistant.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
