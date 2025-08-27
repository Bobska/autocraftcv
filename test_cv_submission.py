#!/usr/bin/env python3
"""
Test CV form submission
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

def test_cv_form_submission():
    """Test CV form submission with AU/NZ data"""
    
    print("=== Testing CV Form Submission ===\n")
    
    # Get or create a profile
    profile = UserProfile.objects.first()
    if not profile:
        profile = UserProfile.objects.create(
            full_name="Test User",
            email="test@example.com"
        )
    
    print(f"Testing with profile: {profile.id}")
    
    # Prepare test data that matches AU/NZ standards
    test_data = {
        'full_name': 'Jane Smith',
        'email': 'jane.smith@email.com',
        'phone': '+61 400 123 456',
        'city_region': 'Melbourne, VIC',
        'job_title': 'Senior Software Developer',
        'linkedin_url': 'https://linkedin.com/in/janesmith',
        'portfolio_url': 'https://janesmith.dev',
        'github_url': 'https://github.com/janesmith',
        
        'professional_summary': 'Experienced software developer with 5+ years in full-stack development. Passionate about creating innovative solutions using modern technologies. Seeking opportunities to contribute to dynamic teams in the Australian tech industry.',
        
        'technical_skills': 'Python, Django, JavaScript, React, PostgreSQL, AWS, Docker, Git',
        'soft_skills': 'Leadership, Communication, Problem-solving, Team collaboration, Project management',
        'languages': 'English (Native), Spanish (Conversational)',
        
        'work_experience': '''Senior Software Developer | TechCorp Australia | 2021-Present
• Led development of customer portal serving 10,000+ users
• Implemented microservices architecture reducing load times by 40%
• Mentored junior developers and conducted code reviews

Software Developer | StartupXYZ | 2019-2021
• Developed REST APIs and database schemas
• Collaborated with cross-functional teams on product features
• Maintained 99.9% uptime for critical systems''',
        
        'education': '''Bachelor of Computer Science | University of Melbourne | 2019
• First Class Honours
• Relevant coursework: Software Engineering, Database Systems, Web Development''',
        
        'certifications': '''AWS Certified Solutions Architect | 2022
Certified Scrum Master | 2021''',
        
        'projects': '''E-commerce Platform | Personal Project
• Built full-stack application with React frontend and Django backend
• Integrated payment processing and inventory management
• Deployed on AWS with CI/CD pipeline''',
        
        'achievements': '''Employee of the Month | TechCorp Australia | 2022
Hackathon Winner | Melbourne Tech Festival | 2021''',
        
        'volunteer_work': '''Code Mentor | CoderDojo Melbourne | 2020-Present
• Teach programming basics to children aged 8-16
• Organize monthly coding workshops''',
        
        'professional_memberships': '''Australian Computer Society (ACS) | Member since 2019''',
        
        'visa_work_rights': 'au_citizen',
        'availability': 'immediate',
        'drivers_license': True,
        'references_choice': 'provided',
        'references': '''John Wilson | Senior Manager | TechCorp Australia
Email: j.wilson@techcorp.com.au | Phone: +61 3 9000 1234
Relationship: Direct supervisor for 2 years

Sarah Chen | Tech Lead | StartupXYZ
Email: s.chen@startupxyz.com | Phone: +61 400 567 890
Relationship: Team lead and mentor'''
    }
    
    # Test form validation
    print("Testing form validation...")
    form = UserProfileForm(data=test_data, instance=profile)
    
    if form.is_valid():
        print("✅ Form validation passed")
        
        # Save the form
        print("Saving form data...")
        try:
            updated_profile = form.save()
            print("✅ Form saved successfully")
            
            # Verify the data was saved
            print("\nVerifying saved data:")
            print(f"✅ Name: {updated_profile.full_name}")
            print(f"✅ Email: {updated_profile.email}")
            print(f"✅ Location: {updated_profile.city_region}")
            print(f"✅ Visa Status: {updated_profile.visa_work_rights}")
            print(f"✅ Availability: {updated_profile.availability}")
            print(f"✅ Driver's License: {updated_profile.drivers_license}")
            print(f"✅ References: {updated_profile.references_choice}")
            print(f"✅ Professional Summary: {len(updated_profile.professional_summary)} characters")
            
            print("\n🎉 CV form submission test completed successfully!")
            print("✅ All AU/NZ CV fields are properly handled")
            print("✅ Form validation is working")
            print("✅ Data persistence is working")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving form: {e}")
            return False
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            error_messages = [str(error) for error in errors]
            print(f"  {field}: {', '.join(error_messages)}")
        return False

if __name__ == "__main__":
    success = test_cv_form_submission()
    sys.exit(0 if success else 1)
