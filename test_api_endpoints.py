#!/usr/bin/env python3
"""
Quick test script to verify the API endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_job_scraping_endpoint():
    """Test the job scraping endpoint with form data"""
    print("🧪 Testing job scraping endpoint...")
    
    # Test with form data (how the JavaScript sends it)
    test_data = {
        'url': 'https://www.linkedin.com/jobs/view/test-job-123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/scrape-with-progress/", data=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'task_id' in data:
                print("✅ Job scraping endpoint working - got task_id!")
                return data['task_id']
            else:
                print("❌ No task_id in response")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        
    return None

def test_progress_endpoint(task_id):
    """Test the progress tracking endpoint"""
    if not task_id:
        print("⏭️ Skipping progress test - no task_id")
        return
        
    print("🧪 Testing progress endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/progress/{task_id}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Progress endpoint working!")
        else:
            print(f"❌ Progress endpoint failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Progress request error: {e}")

def test_resume_upload_endpoint():
    """Test the resume parsing endpoint"""
    print("🧪 Testing resume upload endpoint...")
    
    # Create a dummy text file to simulate resume upload
    dummy_file_content = b"John Doe\\nSoftware Engineer\\nPython, Django, JavaScript"
    
    files = {
        'resume_file': ('test_resume.txt', dummy_file_content, 'text/plain')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/parse-resume-with-progress/", files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'task_id' in data:
                print("✅ Resume upload endpoint working - got task_id!")
                return data['task_id']
            else:
                print("❌ No task_id in response")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        
    return None

def main():
    print("🚀 Testing AutoCraftCV API Endpoints")
    print("=" * 50)
    
    # Test job scraping
    job_task_id = test_job_scraping_endpoint()
    print()
    
    # Test progress tracking
    test_progress_endpoint(job_task_id)
    print()
    
    # Test resume upload
    resume_task_id = test_resume_upload_endpoint()
    print()
    
    # Test progress for resume if we got a task_id
    if resume_task_id:
        print("🧪 Testing resume progress...")
        test_progress_endpoint(resume_task_id)
    
    print("=" * 50)
    print("🎯 Test Summary:")
    print("- If you see ✅ for all tests, the 400 errors are fixed!")
    print("- If you see ❌, there are still issues to resolve.")
    print("- Check the Django server logs for more details.")

if __name__ == "__main__":
    main()
