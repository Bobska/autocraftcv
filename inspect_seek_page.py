#!/usr/bin/env python
"""
Diagnostic script to inspect SEEK page structure
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocraftcv.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def inspect_seek_page():
    """Inspect the actual SEEK page structure"""
    
    test_url = "https://www.seek.com.au/job/78792139?type=standard&userqueryid=8b49dfb2c71af01b59c5e2c5b7bb2cad-2551651"
    
    print("🔍 SEEK Page Structure Inspector")
    print("=" * 60)
    print(f"URL: {test_url}")
    print()
    
    driver = None
    try:
        # Initialize stealth Chrome driver
        print("🚀 Initializing stealth Chrome driver...")
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = uc.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("📄 Loading page...")
        driver.get(test_url)
        
        # Wait and add human-like delay
        time.sleep(5)
        
        # Check page title
        page_title = driver.title
        print(f"📋 Page Title: {page_title}")
        
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print()
        print("🎯 Available Data Attributes:")
        
        # Find all elements with data-automation attributes
        automation_elements = soup.find_all(attrs={"data-automation": True})
        automation_attrs = set()
        for elem in automation_elements:
            if hasattr(elem, 'attrs') and 'data-automation' in elem.attrs:
                automation_attrs.add(elem.attrs['data-automation'])
        
        print("data-automation attributes found:")
        for attr in sorted(automation_attrs):
            print(f"  - [data-automation=\"{attr}\"]")
            
        print()
        
        # Find all elements with data-testid attributes
        testid_elements = soup.find_all(attrs={"data-testid": True})
        testid_attrs = set()
        for elem in testid_elements:
            if hasattr(elem, 'attrs') and 'data-testid' in elem.attrs:
                testid_attrs.add(elem.attrs['data-testid'])
        
        print("data-testid attributes found:")
        for attr in sorted(testid_attrs):
            print(f"  - [data-testid=\"{attr}\"]")
            
        print()
        
        # Check for specific content
        print("🎯 Content Analysis:")
        
        # Look for job title
        title_text = ""
        h1_elements = soup.find_all('h1')
        if h1_elements:
            title_text = h1_elements[0].get_text(strip=True)
            print(f"First H1: {title_text}")
        
        # Look for any text containing "Graduate IT"
        if "Graduate IT" in page_source:
            print("✅ Contains 'Graduate IT' text")
        else:
            print("❌ Does not contain 'Graduate IT' text")
            
        # Check if this is an error page
        if "Page Not Found" in page_source or "404" in page_source:
            print("❌ This appears to be a 404/error page")
        elif "Job has expired" in page_source or "no longer available" in page_source:
            print("❌ Job posting has expired or is no longer available")
        else:
            print("✅ Page appears to be a valid job posting")
            
        print()
        print("📊 Page Statistics:")
        print(f"  - Page size: {len(page_source):,} characters")
        print(f"  - Number of data-automation attributes: {len(automation_attrs)}")
        print(f"  - Number of data-testid attributes: {len(testid_attrs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if driver:
            driver.quit()
            
    print()
    print("🏁 Inspection Complete!")

if __name__ == "__main__":
    inspect_seek_page()
