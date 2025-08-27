"""Debug script to check available selectors on SEEK page."""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_selectors():
    # Initialize Chrome
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    
    driver = uc.Chrome(options=options)
    
    try:
        url = "https://www.seek.com.au/job/86474131"
        print(f"🔄 Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Test company selectors
        company_selectors = [
            '[data-automation="advertiser-name"]',
            '[data-automation="job-detail-company-name"]',
            '[data-testid="job-detail-company"]',
            '.company-name',
            '[data-automation="job-company-name"]',
        ]
        
        print("\n🏢 Testing Company Selectors:")
        print("-" * 50)
        for selector in company_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    print(f"✅ {selector}: '{text}'")
                else:
                    print(f"❌ {selector}: Not found")
            except Exception as e:
                print(f"❌ {selector}: Error - {e}")
        
        # Test description selectors
        description_selectors = [
            '[data-automation="jobAdDetails"]',
            '[data-automation="job-detail-description"]',
            '[data-testid="job-description"]',
            '.job-description',
            '[data-automation="jobDescription"]',
        ]
        
        print("\n📄 Testing Description Selectors:")
        print("-" * 50)
        for selector in description_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()[:100]  # First 100 chars
                    print(f"✅ {selector}: '{text}...'")
                else:
                    print(f"❌ {selector}: Not found")
            except Exception as e:
                print(f"❌ {selector}: Error - {e}")
        
        # Look for any elements containing "SDSI"
        print("\n🔍 Looking for SDSI text:")
        print("-" * 50)
        sdsi_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'SDSI')]")
        for i, elem in enumerate(sdsi_elements[:5]):  # First 5 matches
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                attrs = driver.execute_script("""
                    var attrs = {};
                    for (var i = 0; i < arguments[0].attributes.length; i++) {
                        var attr = arguments[0].attributes[i];
                        attrs[attr.nodeName] = attr.nodeValue;
                    }
                    return attrs;
                """, elem)
                print(f"  {i+1}. <{tag}> '{text}' - Attributes: {attrs}")
            except Exception as e:
                print(f"  {i+1}. Error reading element: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selectors()
