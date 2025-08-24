"""
Enhanced LinkedIn Authentication Bypass Scraper
Implements multiple bypass strategies for LinkedIn job scraping
"""

import time
import re
import logging
import random
import json
from typing import Dict, Optional, Tuple, List
from urllib.parse import urlparse, parse_qs
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LinkedInBypassScraper:
    """
    Enhanced LinkedIn scraper with multiple authentication bypass strategies
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.driver = None
        self.session = requests.Session()
        self.bypass_methods = [
            self._method_mobile_version,
            self._method_google_cache,
            self._method_archive_org,
            self._method_requests_bypass,
            self._method_selenium_stealth,
            self._method_iframe_extraction
        ]
        
    def scrape_linkedin_job(self, url: str) -> Tuple[Dict, str]:
        """
        Main method to scrape LinkedIn job with multiple bypass strategies
        """
        logger.info(f"Starting enhanced LinkedIn bypass scraping for: {url}")
        
        # Extract job ID for alternative URL strategies
        job_id = self._extract_job_id(url)
        
        # Try each bypass method in order of preference
        for i, method in enumerate(self.bypass_methods):
            try:
                logger.info(f"Trying bypass method {i+1}/{len(self.bypass_methods)}: {method.__name__}")
                
                job_data, method_name = method(url, job_id)
                
                if self._validate_extraction(job_data):
                    logger.info(f"Successfully extracted job data using {method_name}")
                    return job_data, method_name
                else:
                    logger.warning(f"Method {method_name} returned insufficient data")
                    
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed: {str(e)}")
                continue
                
        # If all methods fail, return enhanced fallback
        logger.warning("All bypass methods failed, returning enhanced fallback")
        return self._create_enhanced_fallback(url, job_id)
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract LinkedIn job ID from URL"""
        try:
            # Pattern 1: /jobs/view/12345678
            match = re.search(r'/jobs/view/(\d+)', url)
            if match:
                return match.group(1)
                
            # Pattern 2: job ID in query parameters
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if 'currentJobId' in query_params:
                return query_params['currentJobId'][0]
                
            logger.warning(f"Could not extract job ID from URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting job ID: {e}")
            return None
    
    def _method_mobile_version(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 1: Try LinkedIn mobile version which often has fewer restrictions
        """
        try:
            # Convert to mobile URL
            if job_id:
                mobile_url = f"https://m.linkedin.com/jobs/view/{job_id}"
            else:
                mobile_url = url.replace('www.linkedin.com', 'm.linkedin.com')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(mobile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_data = self._extract_from_mobile_html(soup, mobile_url)
                
                if job_data.get('title'):
                    return job_data, 'mobile_bypass'
                    
        except Exception as e:
            logger.warning(f"Mobile version method failed: {e}")
            
        raise Exception("Mobile version method failed")
    
    def _method_google_cache(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 2: Try Google Cache version of the page
        """
        try:
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Referer': 'https://www.google.com/',
            }
            
            response = self.session.get(cache_url, headers=headers, timeout=15)
            
            if response.status_code == 200 and 'cache:' in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_data = self._extract_from_html(soup, url)
                
                if job_data.get('title'):
                    return job_data, 'google_cache_bypass'
                    
        except Exception as e:
            logger.warning(f"Google cache method failed: {e}")
            
        raise Exception("Google cache method failed")
    
    def _method_archive_org(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 3: Try Internet Archive Wayback Machine
        """
        try:
            # Check if page is archived
            availability_url = f"https://archive.org/wayback/available?url={url}"
            
            response = self.session.get(availability_url, timeout=10)
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                archived_url = data['archived_snapshots']['closest']['url']
                
                archive_response = self.session.get(archived_url, timeout=15)
                if archive_response.status_code == 200:
                    soup = BeautifulSoup(archive_response.content, 'html.parser')
                    job_data = self._extract_from_html(soup, url)
                    
                    if job_data.get('title'):
                        return job_data, 'archive_org_bypass'
                        
        except Exception as e:
            logger.warning(f"Archive.org method failed: {e}")
            
        raise Exception("Archive.org method failed")
    
    def _method_requests_bypass(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 4: Advanced requests with multiple user agents and headers
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        for attempt, ua in enumerate(user_agents):
            try:
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
                }
                
                # Add random delay between attempts
                if attempt > 0:
                    time.sleep(random.uniform(2, 5))
                
                response = self.session.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check if we hit auth wall
                    if not self._detect_auth_wall_in_html(soup):
                        job_data = self._extract_from_html(soup, url)
                        
                        if job_data.get('title'):
                            return job_data, f'requests_bypass_ua_{attempt+1}'
                            
            except Exception as e:
                logger.warning(f"Requests bypass attempt {attempt+1} failed: {e}")
                continue
                
        raise Exception("Requests bypass method failed")
    
    def _method_selenium_stealth(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 5: Advanced Selenium with maximum stealth features
        """
        try:
            self._setup_stealth_driver()
            
            # Navigate with random delays and human-like behavior
            self.driver.get("https://www.linkedin.com")
            time.sleep(random.uniform(2, 4))
            
            # Simulate some browsing behavior
            self.driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(random.uniform(1, 2))
            
            # Navigate to job URL
            self.driver.get(url)
            
            # Wait for page load with multiple strategies
            self._wait_for_page_load()
            
            # Check for auth wall and try to bypass
            if self._detect_auth_wall_selenium():
                logger.info("Auth wall detected, trying stealth bypass techniques")
                
                # Try clicking "Guest" mode if available
                self._try_guest_mode()
                
                # Try scrolling to trigger content load
                self._simulate_human_scrolling()
                
                # Wait for dynamic content
                time.sleep(3)
            
            # Extract job data
            job_data = self._extract_from_selenium()
            
            if job_data.get('title'):
                return job_data, 'selenium_stealth_bypass'
                
        except Exception as e:
            logger.warning(f"Selenium stealth method failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
        raise Exception("Selenium stealth method failed")
    
    def _method_iframe_extraction(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """
        Method 6: Try extracting from embedded/iframe versions
        """
        try:
            if not job_id:
                raise Exception("Job ID required for iframe extraction")
            
            # Try LinkedIn's embed API
            embed_url = f"https://www.linkedin.com/embed/jobs/{job_id}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Referer': 'https://example.com/',  # Fake external referer
            }
            
            response = self.session.get(embed_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_data = self._extract_from_html(soup, url)
                
                if job_data.get('title'):
                    return job_data, 'iframe_embed_bypass'
                    
        except Exception as e:
            logger.warning(f"Iframe extraction method failed: {e}")
            
        raise Exception("Iframe extraction method failed")
    
    def _setup_stealth_driver(self):
        """Setup highly stealthy Selenium driver"""
        if self.driver:
            return
            
        try:
            options = uc.ChromeOptions()
            
            # Basic stealth options (compatible with latest Chrome)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            # Randomize window size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Random user agent
            options.add_argument(f'--user-agent={self.ua.random}')
            
            # Use newer experimental options syntax
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Block images for faster loading
                    "plugins": 2,
                    "popups": 2,
                    "geolocation": 2,
                    "notifications": 2,
                    "media_stream": 2,
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth scripts after driver creation
            stealth_scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                "window.chrome = {runtime: {}}",
            ]
            
            for script in stealth_scripts:
                try:
                    self.driver.execute_script(script)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to setup stealth driver: {e}")
            raise
    
    def _wait_for_page_load(self):
        """Wait for page to load with multiple strategies"""
        try:
            # Wait for body
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for content to load
            time.sleep(3)
            
            # Wait for specific LinkedIn elements
            selectors_to_wait = [
                'h1',
                '.jobs-unified-top-card__job-title',
                '.job-details-jobs-unified-top-card__job-title',
                '.jobs-details__main-content'
            ]
            
            for selector in selectors_to_wait:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Page load wait failed: {e}")
    
    def _detect_auth_wall_selenium(self) -> bool:
        """Detect authentication wall using Selenium"""
        auth_indicators = [
            'sign in to see',
            'join to view',
            'sign up',
            'authentication required',
            'login to continue',
            'member login'
        ]
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            return any(indicator in page_text for indicator in auth_indicators)
        except:
            return False
    
    def _detect_auth_wall_in_html(self, soup: BeautifulSoup) -> bool:
        """Detect authentication wall in HTML content"""
        auth_indicators = [
            'sign in to see',
            'join to view',
            'sign up',
            'authentication required',
            'login to continue',
            'member login'
        ]
        
        text_content = soup.get_text().lower()
        return any(indicator in text_content for indicator in auth_indicators)
    
    def _try_guest_mode(self):
        """Try to activate guest mode if available"""
        try:
            guest_selectors = [
                'button[data-tracking-control-name="guest_homepage-basic_guest-homepage-jobs-cta"]',
                '.guest-cta',
                'a[href*="guest"]',
                'button:contains("Continue as guest")'
            ]
            
            for selector in guest_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(2)
                        return True
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Guest mode activation failed: {e}")
        
        return False
    
    def _simulate_human_scrolling(self):
        """Simulate human-like scrolling behavior"""
        try:
            # Random scrolling pattern
            for _ in range(3):
                scroll_amount = random.randint(200, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.5))
                
            # Scroll back up a bit
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.debug(f"Human scrolling simulation failed: {e}")
    
    def _extract_from_mobile_html(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract job data from mobile HTML"""
        job_data = {
            'url': url,
            'title': None,
            'company': None,
            'location': None,
            'description': None,
            'employment_type': None,
            'salary_range': None,
            'requirements': None,
            'responsibilities': None,
            'application_instructions': None,
            'raw_content': soup.get_text()
        }
        
        # Mobile-specific selectors
        title_selectors = [
            'h1',
            '.job-title',
            '.topcard__title',
            '[data-test-id="job-title"]'
        ]
        
        company_selectors = [
            '.topcard__org-name-link',
            '.company-name',
            'a[data-test-id="job-poster-name"]'
        ]
        
        location_selectors = [
            '.topcard__flavor--metadata',
            '.job-criteria__text',
            '.topcard__flavor'
        ]
        
        # Extract title
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                job_data['title'] = element.get_text(strip=True)
                break
        
        # Extract company
        for selector in company_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                job_data['company'] = element.get_text(strip=True)
                break
        
        # Extract location
        for selector in location_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if self._is_location_text(text):
                    job_data['location'] = text
                    break
        
        # Extract description
        description_selectors = [
            '.description',
            '.job-description',
            '.job-details',
            '.show-more-less-html__markup'
        ]
        
        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                job_data['description'] = element.get_text(strip=True)
                break
        
        return job_data
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract job data from regular HTML"""
        job_data = {
            'url': url,
            'title': None,
            'company': None,
            'location': None,
            'description': None,
            'employment_type': None,
            'salary_range': None,
            'requirements': None,
            'responsibilities': None,
            'application_instructions': None,
            'raw_content': soup.get_text()
        }
        
        # Regular LinkedIn selectors
        title_selectors = [
            'h1.top-card-layout__title',
            'h1[data-test-id="job-title"]',
            '.jobs-unified-top-card__job-title h1',
            '.job-details-jobs-unified-top-card__job-title h1',
            'h1.t-24.t-bold.jobs-unified-top-card__job-title',
            '.jobs-details__main-content h1'
        ]
        
        company_selectors = [
            '.jobs-unified-top-card__company-name a',
            '.jobs-unified-top-card__company-name',
            'a[data-test-id="job-posting-company-name"]',
            '.jobs-details-top-card__company-info a'
        ]
        
        # Extract using selectors
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                job_data['title'] = element.get_text(strip=True)
                break
        
        for selector in company_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                job_data['company'] = element.get_text(strip=True)
                break
        
        # Extract description
        description_element = soup.select_one('.show-more-less-html__markup, .jobs-description, .description')
        if description_element:
            job_data['description'] = description_element.get_text(strip=True)
        
        return job_data
    
    def _extract_from_selenium(self) -> Dict:
        """Extract job data using Selenium"""
        job_data = {
            'title': None,
            'company': None,
            'location': None,
            'description': None,
            'employment_type': None,
            'salary_range': None,
            'requirements': None,
            'responsibilities': None,
            'application_instructions': None,
            'raw_content': None
        }
        
        try:
            # Extract title
            title_selectors = [
                'h1.top-card-layout__title',
                'h1[data-test-id="job-title"]',
                '.jobs-unified-top-card__job-title h1',
                '.job-details-jobs-unified-top-card__job-title h1'
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        job_data['title'] = element.text.strip()
                        break
                except:
                    continue
            
            # Extract company
            company_selectors = [
                '.jobs-unified-top-card__company-name a',
                '.jobs-unified-top-card__company-name',
                'a[data-test-id="job-posting-company-name"]'
            ]
            
            for selector in company_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        job_data['company'] = element.text.strip()
                        break
                except:
                    continue
            
            # Extract description
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, '.show-more-less-html__markup, .jobs-description')
                job_data['description'] = desc_element.text.strip()
            except:
                pass
            
            # Get raw content
            try:
                job_data['raw_content'] = self.driver.find_element(By.TAG_NAME, 'body').text
            except:
                pass
                
        except Exception as e:
            logger.error(f"Selenium extraction failed: {e}")
        
        return job_data
    
    def _is_location_text(self, text: str) -> bool:
        """Check if text looks like a location"""
        if not text or len(text) > 100:
            return False
            
        location_indicators = [
            'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
            'remote', 'hybrid', 'on-site', 'city', 'suburb'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in location_indicators)
    
    def _validate_extraction(self, job_data: Dict) -> bool:
        """Validate if extraction was successful"""
        required_fields = ['title', 'company']
        
        for field in required_fields:
            if not job_data.get(field) or len(job_data[field].strip()) < 2:
                return False
        
        # Check for extraction failure indicators
        failure_indicators = [
            'extraction failed',
            'authentication required',
            'login required',
            'sign in to see'
        ]
        
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        for indicator in failure_indicators:
            if indicator in title or indicator in description:
                return False
        
        return True
    
    def _create_enhanced_fallback(self, url: str, job_id: Optional[str]) -> Tuple[Dict, str]:
        """Create enhanced fallback with helpful information"""
        fallback_data = {
            'title': 'LinkedIn Authentication Bypass Required',
            'company': 'LinkedIn Access Limited',
            'location': None,
            'description': f'''LinkedIn has restricted access to this job posting: {url}

This typically happens when LinkedIn detects automated requests. Here are your options:

1. Manual Copy/Paste: Visit the URL in your browser and copy the job content manually
2. Browser Extension: Use a browser extension to extract job data
3. Try Later: LinkedIn's restrictions may be temporary
4. Alternative Sources: Look for the same job on company websites or other job boards

Job ID: {job_id if job_id else 'Not available'}''',
            'requirements': None,
            'responsibilities': None,
            'salary_range': None,
            'employment_type': None,
            'application_instructions': 'Visit the original LinkedIn URL to apply',
            'raw_content': 'LinkedIn access restricted - multiple bypass methods attempted',
            'requires_manual_entry': True,
            'bypass_methods_attempted': len(self.bypass_methods),
            'job_id': job_id,
            'url': url
        }
        
        return fallback_data, 'linkedin_bypass_all_failed'
