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
    """Test the progress tracking endpoint and check for job_id on completion"""
    if not task_id:
        print("⏭️ Skipping progress test - no task_id")
        return
        
    print("🧪 Testing progress endpoint and waiting for completion...")
    
    max_attempts = 30  # Wait up to 60 seconds
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/api/progress/{task_id}/")
            print(f"Attempt {attempt + 1}: Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Progress: {data.get('progress', 0)}% - {data.get('status', '')}")
                
                # Check if completed
                if data.get('completed', False):
                    print("✅ Task completed!")
                    print(f"Final response: {response.text}")
                    
                    # Check for job_id in completed response
                    if 'job_id' in data:
                        print(f"✅ Found job_id: {data['job_id']}")
                        return data['job_id']
                    else:
                        print("❌ No job_id found in completion response")
                        return None
                        
            else:
                print(f"❌ Progress endpoint failed with status {response.status_code}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Progress request error: {e}")
            break
            
        attempt += 1
        time.sleep(2)  # Wait 2 seconds between attempts
    
    print(f"⏰ Timed out waiting for task completion after {max_attempts * 2} seconds")
    return None

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
    print("🚀 Testing AutoCraftCV API Endpoints - job_id Fix Verification")
    print("=" * 60)
    
    # Test job scraping
    job_task_id = test_job_scraping_endpoint()
    print()
    
    # Test progress tracking and wait for completion
    job_id = test_progress_endpoint(job_task_id)
    print()
    
    if job_id:
        print(f"🎉 SUCCESS: Got job_id '{job_id}' - redirect will work!")
        test_url = f"{BASE_URL}/job/{job_id}/"
        print(f"🔗 Testing job detail URL: {test_url}")
        
        try:
            response = requests.get(test_url)
            if response.status_code == 200:
                print("✅ Job detail page accessible!")
            else:
                print(f"⚠️ Job detail page returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing job detail page: {e}")
    else:
        print("❌ FAILED: No job_id received - redirect will still show 'undefined'")
    
    print()
    
    # Test resume upload
    resume_task_id = test_resume_upload_endpoint()
    print()
    
    # Test progress for resume if we got a task_id
    if resume_task_id:
        print("🧪 Testing resume progress and waiting for completion...")
        profile_id = test_progress_endpoint_resume(resume_task_id)
        
        if profile_id:
            print(f"🎉 SUCCESS: Got profile_id '{profile_id}' - redirect will work!")
        else:
            print("❌ FAILED: No profile_id received")
    
    print("=" * 60)
    print("🎯 Fix Verification Summary:")
    print("- If you see job_id and profile_id values, the 'undefined' error is FIXED!")
    print("- If you see ❌ for job_id/profile_id, the issue still exists.")
    print("- Check that the progress completion data includes the IDs.")

def test_progress_endpoint_resume(task_id):
    """Test resume progress endpoint and check for profile_id"""
    if not task_id:
        return None
        
    print("🧪 Testing resume progress endpoint...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/api/progress/{task_id}/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Progress: {data.get('progress', 0)}% - {data.get('status', '')}")
                
                if data.get('completed', False):
                    print("✅ Resume parsing completed!")
                    
                    if 'profile_id' in data:
                        print(f"✅ Found profile_id: {data['profile_id']}")
                        return data['profile_id']
                    else:
                        print("❌ No profile_id found in completion response")
                        return None
                        
        except Exception as e:
            print(f"❌ Error: {e}")
            break
            
        attempt += 1
        time.sleep(2)
    
    return None

if __name__ == "__main__":
    main()
