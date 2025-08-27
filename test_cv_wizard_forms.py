#!/usr/bin/env python3
"""
Test script to verify CV wizard forms are working correctly
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from django.contrib.auth.models import User
from jobassistant.models import UserProfile, Skill, WorkExperience, Education
from jobassistant.forms import PersonalInfoForm, ProfessionalProfileForm, SkillsForm, WorkExperienceWizardForm, EducationWizardForm

def test_forms():
    print("🚀 Testing CV Wizard Forms...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    print(f"✅ Test user: {user.username} ({'created' if created else 'exists'})")
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    print(f"✅ User profile: {profile.id} ({'created' if created else 'exists'})")
    
    # Test 1: PersonalInfoForm (ModelForm)
    print("\n📝 Testing PersonalInfoForm...")
    personal_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'mobile_phone': '+1234567890',
        'address_line_1': '123 Main Street',
        'city': 'Auckland',
        'state_region': 'Auckland',
        'postal_code': '1010',
        'country': 'New Zealand'
    }
    
    personal_form = PersonalInfoForm(personal_data, instance=profile)
    if personal_form.is_valid():
        saved_profile = personal_form.save()
        print(f"✅ PersonalInfoForm saved: {saved_profile.first_name} {saved_profile.last_name}")
    else:
        print(f"❌ PersonalInfoForm errors: {personal_form.errors}")
    
    # Test 2: ProfessionalProfileForm (ModelForm)
    print("\n📝 Testing ProfessionalProfileForm...")
    professional_data = {
        'professional_summary': 'Experienced software engineer with 5+ years in web development.',
        'career_objectives': 'Seeking senior developer role',
        'target_industry': 'technology',
        'years_experience': 5,
        'employment_status': 'employed',
        'availability': 'immediate'
    }
    
    professional_form = ProfessionalProfileForm(professional_data, instance=profile)
    if professional_form.is_valid():
        saved_profile = professional_form.save()
        print(f"✅ ProfessionalProfileForm saved: {saved_profile.professional_summary[:50]}...")
    else:
        print(f"❌ ProfessionalProfileForm errors: {professional_form.errors}")
    
    # Test 3: SkillsForm (Custom Form with save method)
    print("\n📝 Testing SkillsForm...")
    skills_data = {
        'technical_skills': 'Python, JavaScript, React, Django, PostgreSQL',
        'soft_skills': 'Leadership, Communication, Problem-solving, Team management'
    }
    
    skills_form = SkillsForm(skills_data, instance=profile)
    if skills_form.is_valid():
        saved_profile = skills_form.save(profile)
        skill_count = profile.skills.count()
        print(f"✅ SkillsForm saved: {skill_count} skills total")
        
        # Print skills for verification
        tech_skills = profile.skills.filter(category='technical')
        soft_skills = profile.skills.filter(category='soft')
        print(f"   Technical: {[s.name for s in tech_skills]}")
        print(f"   Soft: {[s.name for s in soft_skills]}")
    else:
        print(f"❌ SkillsForm errors: {skills_form.errors}")
    
    # Test 4: WorkExperienceWizardForm (Custom Form with save method)
    print("\n📝 Testing WorkExperienceWizardForm...")
    work_data = {
        'job_title': 'Senior Software Engineer',
        'company_name': 'Tech Solutions Ltd',
        'company_location': 'Auckland, New Zealand',
        'employment_type': 'full_time',
        'start_date': '2020-01-01',
        'currently_working': True,
        'key_responsibilities': 'Lead development team\nArchitect software solutions\nMentor junior developers',
        'key_achievements': 'Increased team productivity by 30%\nDelivered 5 major projects on time'
    }
    
    work_form = WorkExperienceWizardForm(work_data, instance=profile)
    if work_form.is_valid():
        saved_work = work_form.save(profile)
        if saved_work:
            print(f"✅ WorkExperienceWizardForm saved: {saved_work.job_title} at {saved_work.company_name}")
        else:
            print("✅ WorkExperienceWizardForm - no data to save")
        work_count = profile.work_experiences.count()
        print(f"   Total work experiences: {work_count}")
    else:
        print(f"❌ WorkExperienceWizardForm errors: {work_form.errors}")
    
    # Test 5: EducationWizardForm (Custom Form with save method)
    print("\n📝 Testing EducationWizardForm...")
    education_data = {
        'degree_type': 'bachelor',
        'field_of_study': 'Computer Science',
        'institution_name': 'University of Auckland',
        'institution_location': 'Auckland, New Zealand',
        'graduation_year': 2018,
        'gpa_grade': '3.8 GPA',
        'relevant_coursework': 'Software Engineering, Database Systems, Web Development',
        'academic_achievements': 'Dean\'s List, Programming Competition Winner'
    }
    
    education_form = EducationWizardForm(education_data, instance=profile)
    if education_form.is_valid():
        saved_education = education_form.save(profile)
        if saved_education:
            print(f"✅ EducationWizardForm saved: {saved_education.degree_type} in {saved_education.field_of_study}")
        else:
            print("✅ EducationWizardForm - no data to save")
        education_count = profile.education_entries.count()
        print(f"   Total education entries: {education_count}")
    else:
        print(f"❌ EducationWizardForm errors: {education_form.errors}")
    
    # Summary
    print("\n📊 Final Profile Summary:")
    print(f"   Name: {profile.first_name} {profile.last_name}")
    print(f"   Email: {profile.email}")
    print(f"   Professional Summary: {profile.professional_summary[:50] if profile.professional_summary else 'None'}...")
    print(f"   Skills: {profile.skills.count()}")
    print(f"   Work Experience: {profile.work_experiences.count()}")
    print(f"   Education: {profile.education_entries.count()}")
    
    print("\n🎉 All form tests completed!")

if __name__ == '__main__':
    test_forms()
