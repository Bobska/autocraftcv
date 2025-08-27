"""Test current SEEK selectors with the working anti-detection scraper setup."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jobassistant.services.anti_detection_scraper import AntiDetectionScraper
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG)

def test_seek_selectors():
    print("🧪 Testing SEEK Selector Extraction")
    print("=" * 60)
    
    url = "https://www.seek.com.au/job/86474131"
    scraper = AntiDetectionScraper()
    
    try:
        # Use the working scraper setup
        driver = scraper.setup_stealth_driver()
        driver.get(url)
        
        # Wait for page to load and apply the same preprocessing
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Apply human-like behavior and script removal like the actual scraper
        scraper.human_like_behavior(driver, "seek.com.au")
        scraper.remove_script_tags(driver)
        
        # Now test the specific selectors
        print("\n🏢 Testing Company Selectors:")
        print("-" * 40)
        
        company_selectors = [
            '[data-automation="advertiser-name"]',
            'span[data-automation="advertiser-name"]',
            'button[class*="ymza4ui"] span[data-automation="advertiser-name"]',
            '[data-automation="job-detail-company-name"]',
            '[data-testid="job-detail-company"]',
        ]
        
        for selector in company_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, elem in enumerate(elements):
                        text = elem.text.strip()
                        if text:
                            print(f"✅ {selector}[{i}]: '{text}'")
                            break
                    else:
                        print(f"⚠️  {selector}: Found {len(elements)} elements but no text")
                else:
                    print(f"❌ {selector}: Not found")
            except Exception as e:
                print(f"❌ {selector}: Error - {e}")
        
        print("\n📄 Testing Description Selectors:")
        print("-" * 40)
        
        description_selectors = [
            '[data-automation="jobAdDetails"]',
            'div[data-automation="jobAdDetails"]',
            '[data-automation="jobAdDetails"] div',
            '[data-automation="job-detail-description"]',
            '[data-testid="job-description"]',
        ]
        
        for selector in description_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    if text:
                        preview = text[:150] + "..." if len(text) > 150 else text
                        print(f"✅ {selector}: '{preview}'")
                    else:
                        print(f"⚠️  {selector}: Found element but no text")
                else:
                    print(f"❌ {selector}: Not found")
            except Exception as e:
                print(f"❌ {selector}: Error - {e}")
        
        # Test the actual extraction method used by the scraper
        print("\n🔧 Testing Actual Extraction Methods:")
        print("-" * 40)
        
        # Test company extraction
        company_result = scraper.extract_by_selectors(driver, company_selectors)
        print(f"Company extraction result: '{company_result}'")
        
        # Test description extraction  
        description_result = scraper.extract_by_selectors(driver, description_selectors)
        if description_result:
            preview = description_result[:200] + "..." if len(description_result) > 200 else description_result
            print(f"Description extraction result: '{preview}'")
        else:
            print("Description extraction result: ''")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_seek_selectors()
