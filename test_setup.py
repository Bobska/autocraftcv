#!/usr/bin/env python
"""
AutoCraftCV Test Script
Quick tests to verify the application is working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from jobassistant.models import JobPosting, UserProfile, GeneratedDocument
        from jobassistant.services.scraping_service import JobScrapingService
        from jobassistant.services.parsing_service import ResumeParsingService
        from jobassistant.services.content_generation_service import ContentGenerationService
        from jobassistant.services.document_generation_service import DocumentGenerationService
        print("✅ All models and services imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connectivity."""
    print("🧪 Testing database...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result == (1,):
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database query returned unexpected result")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_models():
    """Test model creation."""
    print("🧪 Testing models...")
    
    try:
        from jobassistant.models import JobPosting, UserProfile, GeneratedDocument, AppSettings
        
        # Test AppSettings
        app_version = AppSettings.get_setting('app_version', 'free')
        print(f"✅ AppSettings loaded: version={app_version}")
        
        # Test creating a user profile
        profile = UserProfile.objects.create(
            session_key="test_session",
            full_name="Test User",
            email="test@example.com",
            technical_skills="Python, Django, Testing"
        )
        print(f"✅ UserProfile created: {profile.full_name}")
        
        # Test creating a job posting
        job = JobPosting.objects.create(
            url="https://example.com/job/1",
            title="Test Developer",
            company="Test Company",
            description="A test job posting"
        )
        print(f"✅ JobPosting created: {job.title}")
        
        # Clean up test data
        profile.delete()
        job.delete()
        
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_services():
    """Test service initialization."""
    print("🧪 Testing services...")
    
    try:
        from jobassistant.services.scraping_service import JobScrapingService
        from jobassistant.services.parsing_service import ResumeParsingService
        from jobassistant.services.content_generation_service import ContentGenerationService
        from jobassistant.services.document_generation_service import DocumentGenerationService
        
        # Test service initialization
        scraper = JobScrapingService()
        parser = ResumeParsingService()
        generator = ContentGenerationService()
        doc_gen = DocumentGenerationService()
        
        print("✅ All services initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def test_forms():
    """Test form creation."""
    print("🧪 Testing forms...")
    
    try:
        from jobassistant.forms import JobURLForm, ResumeUploadForm, UserProfileForm, DocumentGenerationForm
        
        # Test form initialization
        url_form = JobURLForm()
        upload_form = ResumeUploadForm()
        profile_form = UserProfileForm()
        doc_form = DocumentGenerationForm()
        
        print("✅ All forms initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Form test error: {e}")
        return False

def test_settings():
    """Test Django settings."""
    print("🧪 Testing settings...")
    
    try:
        from django.conf import settings
        
        # Check critical settings
        assert hasattr(settings, 'SECRET_KEY'), "SECRET_KEY not found"
        assert hasattr(settings, 'DEBUG'), "DEBUG not found"
        assert hasattr(settings, 'DATABASES'), "DATABASES not found"
        assert hasattr(settings, 'INSTALLED_APPS'), "INSTALLED_APPS not found"
        
        # Check if our app is installed
        assert 'jobassistant' in settings.INSTALLED_APPS, "jobassistant app not in INSTALLED_APPS"
        
        print("✅ Settings configuration verified")
        return True
    except Exception as e:
        print(f"❌ Settings test error: {e}")
        return False

def test_urls():
    """Test URL configuration."""
    print("🧪 Testing URLs...")
    
    try:
        from django.urls import reverse
        
        # Test URL reversing
        home_url = reverse('jobassistant:home')
        print(f"✅ Home URL: {home_url}")
        
        return True
    except Exception as e:
        print(f"❌ URL test error: {e}")
        return False

def test_templates():
    """Test template loading."""
    print("🧪 Testing templates...")
    
    try:
        from django.template.loader import get_template
        
        # Test loading key templates
        templates = [
            'jobassistant/base.html',
            'jobassistant/home.html',
            'jobassistant/job_details.html'
        ]
        
        for template_name in templates:
            template = get_template(template_name)
            print(f"✅ Template loaded: {template_name}")
        
        return True
    except Exception as e:
        print(f"❌ Template test error: {e}")
        return False

def run_basic_functionality_test():
    """Test basic application functionality."""
    print("🧪 Testing basic functionality...")
    
    try:
        from jobassistant.models import AppSettings
        from jobassistant.services.scraping_service import JobScrapingService
        
        # Test settings
        app_version = AppSettings.get_setting('app_version', 'free')
        print(f"✅ App version: {app_version}")
        
        # Test scraping service initialization
        scraper = JobScrapingService()
        print(f"✅ Scraping service initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AutoCraftCV Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Models", test_models),
        ("Services", test_services),
        ("Forms", test_forms),
        ("Settings", test_settings),
        ("URLs", test_urls),
        ("Templates", test_templates),
        ("Basic Functionality", run_basic_functionality_test),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! AutoCraftCV is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Start the development server: python manage.py runserver")
        print("   2. Open browser to: http://127.0.0.1:8000")
        print("   3. Test the web interface")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Common solutions:")
        print("   - Make sure virtual environment is activated")
        print("   - Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   - Run database migrations: python manage.py migrate")
        print("   - Check .env file configuration")
        return False

if __name__ == "__main__":
    main()
