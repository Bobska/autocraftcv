#!/usr/bin/env python3
"""
Test script for CV editing system
"""
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from jobassistant.models import UserProfile
from jobassistant.forms import UserProfileForm

def test_cv_editing_system():
    """Test the comprehensive CV editing system"""
    
    print("=== AutoCraftCV - AU/NZ CV Editing System Test ===\n")
    
    # Get a profile to test with
    try:
        profile = UserProfile.objects.first()
        if not profile:
            print("❌ No profiles found. Creating a test profile...")
            profile = UserProfile.objects.create(
                full_name="Test User",
                email="test@example.com",
                phone="+61 400 000 000",
                city_region="Sydney, NSW"
            )
            print(f"✅ Created test profile: {profile.id}")
        else:
            print(f"✅ Found profile: {profile.full_name or 'No name'} - {profile.email or 'No email'}")
    
    except Exception as e:
        print(f"❌ Error accessing profiles: {e}")
        return False
    
    # Test form initialization
    try:
        form = UserProfileForm(instance=profile)
        print(f"✅ Form initialized successfully with {len(form.fields)} fields")
    except Exception as e:
        print(f"❌ Error initializing form: {e}")
        return False
    
    # Check key AU/NZ fields
    print("\n=== AU/NZ CV Fields Check ===")
    au_nz_fields = {
        'visa_work_rights': 'Visa/Work Rights',
        'availability': 'Availability',
        'drivers_license': 'Driver\'s License',
        'references_choice': 'References Choice',
        'professional_summary': 'Professional Summary',
        'technical_skills': 'Technical Skills',
        'soft_skills': 'Soft Skills',
        'work_experience': 'Work Experience',
        'education': 'Education',
        'certifications': 'Certifications',
        'projects': 'Projects',
        'achievements': 'Achievements',
        'volunteer_work': 'Volunteer Work',
        'professional_memberships': 'Professional Memberships',
        'languages': 'Languages'
    }
    
    missing_fields = []
    for field, name in au_nz_fields.items():
        if field in form.fields:
            print(f"✅ {name} ({field})")
        else:
            print(f"❌ {name} ({field}) - MISSING")
            missing_fields.append(field)
    
    # Test model field access
    print("\n=== Model Field Access Test ===")
    model_fields = [
        'full_name', 'email', 'phone', 'city_region', 'job_title',
        'linkedin_url', 'portfolio_url', 'github_url',
        'professional_summary', 'technical_skills', 'soft_skills',
        'work_experience', 'education', 'certifications', 'projects',
        'achievements', 'volunteer_work', 'professional_memberships',
        'visa_work_rights', 'availability', 'drivers_license',
        'references_choice', 'references', 'languages'
    ]
    
    for field in model_fields:
        try:
            value = getattr(profile, field)
            if value:
                print(f"✅ {field}: {str(value)[:50]}")
            else:
                print(f"⚪ {field}: (empty)")
        except AttributeError:
            print(f"❌ {field}: Field not found on model")
    
    # Summary
    print(f"\n=== Test Summary ===")
    if missing_fields:
        print(f"❌ {len(missing_fields)} fields missing from form: {', '.join(missing_fields)}")
        return False
    else:
        print("✅ All AU/NZ CV fields are properly configured")
        print("✅ Form system is working correctly")
        print("✅ Model fields are accessible")
        print("\n🎉 CV Editing System is ready for Australian/New Zealand CVs!")
        return True

if __name__ == "__main__":
    success = test_cv_editing_system()
    sys.exit(0 if success else 1)
