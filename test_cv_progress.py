import requests
import json
import time

# Test the CV upload with progress functionality
BASE_URL = "http://127.0.0.1:8000"

def test_cv_upload_progress():
    print("🔄 Testing CV upload with progress tracking...")
    
    # First, get the CV upload page to get CSRF token
    session = requests.Session()
    upload_page = session.get(f"{BASE_URL}/cv/upload/")
    print(f"📄 CV upload page status: {upload_page.status_code}")
    
    if upload_page.status_code != 200:
        print("❌ Failed to access CV upload page")
        return
    
    # Extract CSRF token (simple extraction)
    csrf_token = None
    if 'csrfmiddlewaretoken' in upload_page.text:
        # Find CSRF token in the HTML
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', upload_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"🔑 CSRF token found: {csrf_token[:20]}...")
    
    if not csrf_token:
        print("❌ Could not find CSRF token")
        return
    
    # Prepare test CV file
    test_cv_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test CV for Upload) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000217 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
309
%%EOF"""
    
    # Upload CV with progress
    files = {'cv_file': ('test_cv.pdf', test_cv_content, 'application/pdf')}
    data = {'csrfmiddlewaretoken': csrf_token}
    
    print("📤 Uploading CV...")
    upload_response = session.post(f"{BASE_URL}/api/cv/upload-with-progress/", 
                                  files=files, 
                                  data=data)
    
    print(f"📤 Upload response status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        try:
            upload_data = upload_response.json()
            print(f"✅ Upload successful: {upload_data}")
            
            if 'task_id' in upload_data:
                task_id = upload_data['task_id']
                print(f"📊 Progress tracking task ID: {task_id}")
                
                # Test progress tracking API
                print("🔄 Testing progress tracking...")
                for i in range(5):
                    progress_response = session.get(f"{BASE_URL}/api/progress/{task_id}/")
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        print(f"📊 Progress {i+1}/5: {progress_data}")
                        
                        if progress_data.get('status') == 'completed':
                            print("✅ Progress tracking completed successfully!")
                            break
                    else:
                        print(f"❌ Progress request failed: {progress_response.status_code}")
                    
                    time.sleep(1)
            else:
                print("❌ No task_id in upload response")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse upload response: {e}")
            print(f"Response text: {upload_response.text[:500]}")
    else:
        print(f"❌ Upload failed: {upload_response.status_code}")
        print(f"Response text: {upload_response.text[:500]}")

if __name__ == "__main__":
    test_cv_upload_progress()
