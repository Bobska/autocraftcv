"""
Test views for debugging scraping functionality
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.enhanced_scraping_service import EnhancedJobScrapingService
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def test_scraping(request):
    """
    Test endpoint for debugging job scraping
    POST data: {"url": "job_url_to_test"}
    """
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'URL is required'
            }, status=400)
        
        logger.info(f"Testing scraping for URL: {url}")
        
        # Test with enhanced scraper
        scraper = EnhancedJobScrapingService()
        job_data, method = scraper.scrape_job(url)
        
        return JsonResponse({
            'success': True,
            'url': url,
            'method_used': method,
            'job_data': job_data,
            'validation': {
                'has_title': bool(job_data.get('title') and len(job_data['title']) > 5),
                'has_company': bool(job_data.get('company') and len(job_data['company']) > 2),
                'has_description': bool(job_data.get('description') and len(job_data['description']) > 50),
                'title_length': len(job_data.get('title', '')),
                'company_length': len(job_data.get('company', '')),
                'description_length': len(job_data.get('description', ''))
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in test_scraping: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def test_scraping_page(request):
    """
    Simple HTML page for testing scraping functionality
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job Scraping Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 4px; background-color: #f9f9f9; }
            .error { border-color: #dc3545; background-color: #f8d7da; }
            .success { border-color: #28a745; background-color: #d4edda; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Job Scraping Test Tool</h1>
        <p>Test the enhanced job scraping functionality by entering a job posting URL below.</p>
        
        <form id="testForm">
            <div class="form-group">
                <label for="url">Job Posting URL:</label>
                <input type="text" id="url" name="url" placeholder="https://example.com/job-posting" required>
            </div>
            <button type="submit">Test Scraping</button>
        </form>
        
        <div id="result" style="display: none;"></div>
        
        <div style="margin-top: 30px;">
            <h3>Test URLs (Examples):</h3>
            <ul>
                <li><a href="#" onclick="testUrl('https://www.linkedin.com/jobs/view/3774394042')">LinkedIn Job Example</a></li>
                <li><a href="#" onclick="testUrl('https://www.indeed.com/viewjob?jk=example')">Indeed Job Example</a></li>
                <li><a href="#" onclick="testUrl('https://www.glassdoor.com/job-listing/example')">Glassdoor Job Example</a></li>
            </ul>
            <p><em>Note: Replace with actual job URLs to test</em></p>
        </div>
        
        <script>
            function testUrl(url) {
                document.getElementById('url').value = url;
            }
            
            document.getElementById('testForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const url = document.getElementById('url').value;
                const resultDiv = document.getElementById('result');
                
                if (!url) {
                    alert('Please enter a URL');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result';
                resultDiv.innerHTML = '<p>Testing scraping... Please wait.</p>';
                
                fetch('/jobassistant/test-scraping/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>Scraping Successful!</h3>
                            <p><strong>Method Used:</strong> ${data.method_used}</p>
                            <p><strong>URL:</strong> ${data.url}</p>
                            
                            <h4>Extracted Data:</h4>
                            <p><strong>Title:</strong> ${data.job_data.title || 'Not extracted'}</p>
                            <p><strong>Company:</strong> ${data.job_data.company || 'Not extracted'}</p>
                            <p><strong>Location:</strong> ${data.job_data.location || 'Not extracted'}</p>
                            <p><strong>Employment Type:</strong> ${data.job_data.employment_type || 'Not extracted'}</p>
                            <p><strong>Salary Range:</strong> ${data.job_data.salary_range || 'Not extracted'}</p>
                            
                            <h4>Validation Results:</h4>
                            <ul>
                                <li>Has Title: ${data.validation.has_title ? '✅ Yes' : '❌ No'} (${data.validation.title_length} chars)</li>
                                <li>Has Company: ${data.validation.has_company ? '✅ Yes' : '❌ No'} (${data.validation.company_length} chars)</li>
                                <li>Has Description: ${data.validation.has_description ? '✅ Yes' : '❌ No'} (${data.validation.description_length} chars)</li>
                            </ul>
                            
                            <h4>Full Job Data:</h4>
                            <pre>${JSON.stringify(data.job_data, null, 2)}</pre>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <h3>Scraping Failed</h3>
                            <p><strong>Error:</strong> ${data.error}</p>
                        `;
                    }
                })
                .catch(error => {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>Request Failed</h3>
                        <p><strong>Error:</strong> ${error.message}</p>
                    `;
                });
            });
        </script>
    </body>
    </html>
    """
    
    from django.http import HttpResponse
    return HttpResponse(html_content)
