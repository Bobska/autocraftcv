#!/usr/bin/env python3
"""
Test the complete CV wizard flow end-to-end using Django test client
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from jobassistant.models import UserProfile
import json

def test_wizard_flow():
    print("🚀 Testing Complete CV Wizard Flow...")
    
    # Create test client
    client = Client()
    
    # Create test user and login
    user, created = User.objects.get_or_create(
        username='wizardtest',
        defaults={'email': 'wizard@test.com', 'password': 'testpass123'}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
    
    print(f"✅ Test user: {user.username}")
    
    # Test Step 1: Personal Information
    print("\n📝 Testing Step 1: Personal Information")
    response = client.post('/cv/create/?step=1', {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@example.com',
        'mobile_phone': '+64212345678',
        'address_line_1': '456 Queen Street',
        'city': 'Wellington',
        'state_region': 'Wellington',
        'postal_code': '6011',
        'country': 'New Zealand'
    })
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                print(f"✅ Step 1 successful: {data.get('message', 'No message')}")
            else:
                print(f"❌ Step 1 failed: {data}")
        except json.JSONDecodeError:
            print(f"❌ Step 1 - Invalid JSON response: {response.content[:200]}")
    else:
        print(f"❌ Step 1 - HTTP {response.status_code}: {response.content[:200]}")
    
    # Test Step 2: Professional Profile
    print("\n📝 Testing Step 2: Professional Profile")
    response = client.post('/cv/create/?step=2', {
        'professional_summary': 'Senior marketing professional with 8+ years experience.',
        'career_objectives': 'Seeking marketing director role',
        'target_industry': 'marketing',
        'years_experience': 8,
        'employment_status': 'employed',
        'availability': 'immediate'
    })
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                print(f"✅ Step 2 successful: {data.get('message', 'No message')}")
            else:
                print(f"❌ Step 2 failed: {data}")
        except json.JSONDecodeError:
            print(f"❌ Step 2 - Invalid JSON response: {response.content[:200]}")
    else:
        print(f"❌ Step 2 - HTTP {response.status_code}: {response.content[:200]}")
    
    # Test Step 3: Skills
    print("\n📝 Testing Step 3: Skills")
    response = client.post('/cv/create/?step=3', {
        'technical_skills': 'SEO, Google Analytics, AdWords, Social Media Marketing',
        'soft_skills': 'Strategic Planning, Team Leadership, Creative Thinking'
    })
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                print(f"✅ Step 3 successful: {data.get('message', 'No message')}")
            else:
                print(f"❌ Step 3 failed: {data}")
        except json.JSONDecodeError:
            print(f"❌ Step 3 - Invalid JSON response: {response.content[:200]}")
    else:
        print(f"❌ Step 3 - HTTP {response.status_code}: {response.content[:200]}")
    
    # Test Step 4: Work Experience
    print("\n📝 Testing Step 4: Work Experience")
    response = client.post('/cv/create/?step=4', {
        'job_title': 'Marketing Manager',
        'company_name': 'Digital Solutions NZ',
        'company_location': 'Wellington, New Zealand',
        'employment_type': 'full_time',
        'start_date': '2019-03-01',
        'currently_working': True,
        'key_responsibilities': 'Manage marketing campaigns\nLead team of 5\nDevelop brand strategy',
        'key_achievements': 'Increased brand awareness by 40%\nGenerated $2M in new revenue'
    })
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                print(f"✅ Step 4 successful: {data.get('message', 'No message')}")
            else:
                print(f"❌ Step 4 failed: {data}")
        except json.JSONDecodeError:
            print(f"❌ Step 4 - Invalid JSON response: {response.content[:200]}")
    else:
        print(f"❌ Step 4 - HTTP {response.status_code}: {response.content[:200]}")
    
    # Test Step 5: Education
    print("\n📝 Testing Step 5: Education")
    response = client.post('/cv/create/?step=5', {
        'degree_type': 'bachelor',
        'field_of_study': 'Marketing and Communications',
        'institution_name': 'Victoria University of Wellington',
        'institution_location': 'Wellington, New Zealand',
        'graduation_year': 2015,
        'gpa_grade': 'A- Average',
        'relevant_coursework': 'Digital Marketing, Consumer Behavior, Brand Management',
        'academic_achievements': 'Dean\'s List 2014-2015, Marketing Society President'
    })
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                if data.get('completed'):
                    print(f"✅ Step 5 completed - CV wizard finished! {data.get('message', '')}")
                    redirect_url = data.get('redirect_url', '')
                    if redirect_url:
                        print(f"   Redirect URL: {redirect_url}")
                else:
                    print(f"✅ Step 5 successful: {data.get('message', 'No message')}")
            else:
                print(f"❌ Step 5 failed: {data}")
        except json.JSONDecodeError:
            print(f"❌ Step 5 - Invalid JSON response: {response.content[:200]}")
    else:
        print(f"❌ Step 5 - HTTP {response.status_code}: {response.content[:200]}")
    
    # Verify data was saved
    print("\n📊 Verifying saved data...")
    try:
        profiles = UserProfile.objects.filter(first_name='Jane', last_name='Smith')
        if profiles.exists():
            profile = profiles.first()
            print(f"✅ Profile found: {profile.first_name} {profile.last_name}")
            print(f"   Email: {profile.email}")
            print(f"   Summary: {profile.professional_summary[:50] if profile.professional_summary else 'None'}...")
            print(f"   Skills: {profile.skills.count()}")
            print(f"   Work Experience: {profile.work_experiences.count()}")
            print(f"   Education: {profile.education_entries.count()}")
        else:
            print("❌ No profile found with test data")
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    
    print("\n🎉 Complete wizard flow test finished!")

if __name__ == '__main__':
    test_wizard_flow()
