"""
Anti-Detection Job Scraper for sites with bot protection (SEEK, etc.)
"""

import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import json
import re
from typing import Dict, Optional, Tuple
from fake_useragent import UserAgent
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AntiDetectionScraper:
    """Enhanced scraper with anti-detection capabilities for protected job sites"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
        # Site-specific configurations
        self.site_configs = {
            'seek.com.au': {
                'wait_time': (5, 10),
                'scroll_behavior': True,
                'mouse_movements': True,
                'selectors': {
                    'title': [
                        '[data-automation="job-detail-title"]',
                        'h1[data-testid="job-title"]',
                        '[data-testid="job-header-title"]',
                        '.job-header h1',
                        'h1',
                    ],
                    'company': [
                        '[data-automation="advertiser-name"]',
                        '[data-automation="job-detail-company-name"]',
                        '[data-testid="job-detail-company"]',
                        '.company-name',
                        '[data-automation="job-company-name"]',
                        'a[href*="/companies/"]',
                    ],
                    'location': [
                        '[data-automation="job-detail-location"]',
                        '[data-testid="job-location"]',
                        '.location',
                        '[data-automation="job-location"]',
                    ],
                    'description': [
                        '[data-automation="jobAdDetails"]',
                        '[data-automation="job-detail-description"]',
                        '[data-testid="job-description"]',
                        '.job-description',
                        '[data-automation="jobDescription"]',
                    ],
                    'requirements': [
                        '[data-automation="job-requirements"]',
                        '.requirements',
                        '.qualifications',
                        '[data-testid="requirements"]',
                    ]
                }
            }
        }
    
    def setup_stealth_driver(self) -> webdriver.Chrome:
        """Setup undetected Chrome driver with stealth capabilities"""
        
        try:
            # Use undetected-chromedriver for better anti-detection
            options = uc.ChromeOptions()
            
            # Basic stealth options
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            
            # Randomize window size to appear more human
            width = random.randint(1200, 1600)
            height = random.randint(800, 1200)
            options.add_argument(f'--window-size={width},{height}')
            
            # Random user agent
            options.add_argument(f'--user-agent={self.ua.random}')
            
            # Create undetected Chrome driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Additional stealth JavaScript injections
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' }),
                    }),
                });
                
                // Remove webdriver property
                delete navigator.__proto__.webdriver;
            """)
            
            self.driver = driver
            logger.info("Stealth Chrome driver initialized successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup stealth driver: {str(e)}")
            raise
    
    def human_like_behavior(self, driver: webdriver.Chrome, site_domain: str = "generic"):
        """Simulate human-like browsing behavior"""
        
        try:
            # Get site-specific configuration
            config = self.site_configs.get(site_domain, {})
            wait_time = config.get('wait_time', (3, 7))
            
            # Random initial delay
            initial_delay = random.uniform(wait_time[0], wait_time[1])
            logger.info(f"Initial human delay: {initial_delay:.2f}s")
            time.sleep(initial_delay)
            
            # Simulate mouse movements if enabled
            if config.get('mouse_movements', True):
                self.simulate_mouse_movements(driver)
            
            # Simulate scrolling behavior if enabled
            if config.get('scroll_behavior', True):
                self.simulate_scrolling(driver)
            
            # Random micro-delays between actions
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.warning(f"Error in human behavior simulation: {str(e)}")
    
    def simulate_mouse_movements(self, driver: webdriver.Chrome):
        """Simulate random mouse movements"""
        try:
            actions = ActionChains(driver)
            
            # Get window size
            window_size = driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            
            # Perform random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                
                actions.move_by_offset(x, y)
                actions.perform()
                time.sleep(random.uniform(0.1, 0.5))
                
                # Reset to center
                actions.move_by_offset(-x, -y)
                actions.perform()
                
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {str(e)}")
    
    def simulate_scrolling(self, driver: webdriver.Chrome):
        """Simulate human-like scrolling behavior"""
        try:
            # Get page height
            page_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            
            # Scroll in chunks with delays
            scroll_chunks = random.randint(3, 6)
            chunk_size = page_height // scroll_chunks
            
            for i in range(scroll_chunks):
                scroll_to = current_position + chunk_size + random.randint(-50, 50)
                
                driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                current_position = scroll_to
                
                # Random pause to simulate reading
                time.sleep(random.uniform(1, 3))
            
            # Scroll back to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {str(e)}")
    
    def detect_anti_bot_protection(self, driver: webdriver.Chrome) -> bool:
        """Detect if the site is showing anti-bot protection"""
        
        try:
            page_source = driver.page_source.lower()
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()
            
            # Common anti-bot indicators
            protection_indicators = [
                'cloudflare',
                'challenge',
                'captcha',
                'verify you are human',
                'prove you\'re not a robot',
                'security check',
                'blocked',
                'access denied',
                'robot verification',
                'checking your browser',
                'ddos protection',
                'rate limited',
                'too many requests',
                'suspicious activity'
            ]
            
            # Check in page content
            for indicator in protection_indicators:
                if indicator in page_source or indicator in page_title:
                    logger.warning(f"Anti-bot protection detected: {indicator}")
                    return True
            
            # Check for redirect to protection pages
            protection_urls = ['challenge', 'captcha', 'blocked', 'denied']
            if any(url_part in current_url for url_part in protection_urls):
                logger.warning(f"Redirected to protection page: {current_url}")
                return True
            
            # Check for minimal content (possible blocking)
            if len(page_source) < 1000:
                logger.warning("Page content suspiciously short - possible blocking")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting anti-bot protection: {str(e)}")
            return True  # Assume protection if we can't detect
    
    def scrape_protected_site(self, url: str) -> Tuple[Dict, str]:
        """Main method to scrape protected job sites"""
        
        logger.info(f"Starting anti-detection scraping for: {url}")
        
        try:
            # Setup stealth driver
            driver = self.setup_stealth_driver()
            
            # Get site domain for configuration
            domain = urlparse(url).netloc.lower()
            site_domain = self.get_site_domain(domain)
            
            logger.info(f"Detected site domain: {site_domain}")
            
            # Navigate to URL
            driver.get(url)
            
            # Human-like behavior
            self.human_like_behavior(driver, site_domain)
            
            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for anti-bot protection
            if self.detect_anti_bot_protection(driver):
                logger.warning("Anti-bot protection detected - manual entry required")
                return self.create_manual_fallback_response(url), "anti_bot_detected"
            
            # Extract job data using site-specific selectors
            job_data = self.extract_job_data(driver, site_domain, url)
            
            # Validate extraction
            if self.is_successful_extraction(job_data):
                logger.info("Successfully extracted job data")
                return job_data, "anti_detection_success"
            else:
                logger.warning("Extraction failed - falling back to manual entry")
                return self.create_manual_fallback_response(url), "extraction_failed"
            
        except Exception as e:
            logger.error(f"Anti-detection scraping failed: {str(e)}")
            return self.create_manual_fallback_response(url), f"error_{str(e)}"
        
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def get_site_domain(self, domain: str) -> str:
        """Identify the site domain for configuration"""
        
        if 'seek.com' in domain:
            return 'seek.com.au'
        elif 'indeed.com' in domain:
            return 'indeed.com'
        elif 'linkedin.com' in domain:
            return 'linkedin.com'
        else:
            return 'generic'
    
    def extract_job_data(self, driver: webdriver.Chrome, site_domain: str, url: str) -> Dict:
        """Extract job data using site-specific selectors"""
        
        # Remove script tags to prevent extraction from JavaScript variables
        self.remove_script_tags(driver)
        
        config = self.site_configs.get(site_domain, {})
        selectors = config.get('selectors', {})
        
        job_data = {
            'title': self.extract_by_selectors(driver, selectors.get('title', [])),
            'company': self.extract_by_selectors(driver, selectors.get('company', [])),
            'location': self.extract_by_selectors(driver, selectors.get('location', [])),
            'description': self.extract_by_selectors(driver, selectors.get('description', [])),
            'requirements': self.extract_by_selectors(driver, selectors.get('requirements', [])),
            'url': url,
            'extraction_method': 'anti_detection_scraper',
            'site_domain': site_domain,
            'raw_content': driver.page_source[:10000]  # First 10k chars for analysis
        }
        
        # Clean and enhance extracted data
        job_data = self.clean_extracted_data(job_data)
        
        return job_data
    
    def remove_script_tags(self, driver: webdriver.Chrome):
        """Remove script tags from the page to prevent extraction from JavaScript variables"""
        try:
            # Execute JavaScript to remove all script tags
            driver.execute_script("""
                var scripts = document.getElementsByTagName('script');
                for (var i = scripts.length - 1; i >= 0; i--) {
                    scripts[i].parentNode.removeChild(scripts[i]);
                }
            """)
            logger.debug("Successfully removed script tags from page")
        except Exception as e:
            logger.debug(f"Failed to remove script tags: {str(e)}")
    
    
    def extract_by_selectors(self, driver: webdriver.Chrome, selectors: list) -> str:
        """Try multiple selectors to extract text"""
        
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                text = element.text.strip()
                if text and len(text) > 2:
                    logger.debug(f"Successfully extracted with selector: {selector}")
                    return text
                    
            except TimeoutException:
                logger.debug(f"Selector timeout: {selector}")
                continue
            except Exception as e:
                logger.debug(f"Selector failed {selector}: {str(e)}")
                continue
        
        return ""
    
    def clean_extracted_data(self, job_data: Dict) -> Dict:
        """Clean and enhance extracted job data"""
        
        # Clean text fields
        for field in ['title', 'company', 'location', 'description', 'requirements']:
            if job_data.get(field):
                # Remove JSON-encoded content that may have been extracted
                job_data[field] = self.remove_json_encoded_content(job_data[field])
                
                # Remove excessive whitespace
                job_data[field] = ' '.join(job_data[field].split())
                
                # Remove common web artifacts
                artifacts = [
                    'Apply Now', 'Apply', 'Save Job', 'Share Job',
                    'Quick Apply', 'Easy Apply', '(opens in new window)',
                    'Back to results', 'View all jobs'
                ]
                
                for artifact in artifacts:
                    job_data[field] = job_data[field].replace(artifact, '')
                
                job_data[field] = job_data[field].strip()
        
        # Set meaningful defaults for empty fields
        if not job_data.get('title'):
            job_data['title'] = 'Title extraction failed - manual entry required'
        
        if not job_data.get('company'):
            job_data['company'] = 'Company extraction failed - manual entry required'
        
        if not job_data.get('description'):
            job_data['description'] = 'Description extraction failed - manual entry required'
        
        return job_data
    
    def remove_json_encoded_content(self, text: str) -> str:
        """Remove JSON-encoded content that may have been incorrectly extracted"""
        if not text:
            return text
            
        # Remove content that contains JSON-encoded HTML (like \u003C for <)
        import re
        
        # Pattern to detect JSON-encoded HTML
        json_encoded_pattern = r'\\u003[A-Fa-f0-9]{1}|\\u002[A-Fa-f0-9]{1}|\\[\'"]'
        
        # If the text contains significant JSON encoding, it's likely from a script tag
        if re.search(json_encoded_pattern, text):
            # Count the occurrences
            encoded_matches = len(re.findall(json_encoded_pattern, text))
            total_length = len(text)
            
            # If more than 5% of the content is JSON-encoded, discard it
            if total_length > 0 and (encoded_matches / total_length * 100) > 0.05:
                return ""
        
        # Remove specific JSON-encoded artifacts
        text = re.sub(r'\\u003C.*?\\u003E', '', text)  # Remove <tag> patterns
        text = re.sub(r'\\u002F', '/', text)  # Convert \u002F to /
        text = re.sub(r'\\[\'"]', '', text)  # Remove escaped quotes
        
        return text.strip()
    
    def is_successful_extraction(self, job_data: Dict) -> bool:
        """Check if extraction was successful"""
        
        # Must have at least title or company
        has_title = bool(job_data.get('title') and 
                        len(job_data['title']) > 10 and 
                        'extraction failed' not in job_data['title'].lower())
        
        has_company = bool(job_data.get('company') and 
                          len(job_data['company']) > 3 and 
                          'extraction failed' not in job_data['company'].lower())
        
        has_description = bool(job_data.get('description') and 
                              len(job_data['description']) > 100 and 
                              'extraction failed' not in job_data['description'].lower())
        
        # Consider successful if we have meaningful data
        return has_title or (has_company and has_description)
    
    def create_manual_fallback_response(self, url: str) -> Dict:
        """Create response indicating manual entry is required"""
        
        return {
            'title': 'Manual Entry Required',
            'company': 'Manual Entry Required',
            'description': f'Automatic extraction failed for URL: {url}. Anti-bot protection detected or extraction failed. Manual content entry is required.',
            'location': 'Manual Entry Required',
            'requirements': 'Manual Entry Required',
            'responsibilities': 'Manual Entry Required',
            'salary_range': '',
            'employment_type': '',
            'url': url,
            'extraction_status': 'manual_required',
            'manual_entry_required': True,
            'anti_bot_detected': True,
            'requires_manual_fallback': True
        }


class SEEKSpecificScraper(AntiDetectionScraper):
    """SEEK.com.au specific scraper with enhanced detection"""
    
    def __init__(self):
        super().__init__()
        
        # SEEK-specific enhanced selectors (updated for 2025)
        self.seek_selectors = {
            'title': [
                '[data-automation="job-detail-title"]',
                'h1[data-testid="job-title"]',
                '[data-testid="job-header-title"]',
                '[data-automation="jobTitle"]',
                'h1[class*="jobTitle"]',
                'h1[id*="jobTitle"]',
                '.JobHeader-title',
                '.job-header h1',
                'h1',
            ],
            'company': [
                '[data-automation="advertiser-name"]',
                '[data-automation="job-detail-company-name"]',
                '[data-testid="job-detail-company"]',
                '[data-automation="job-company-name"]',
                '[data-testid="company-name"]',
                'a[href*="/companies/"]',
                '.company-name',
                '[class*="company"]',
                '.JobHeader-company',
            ],
            'location': [
                '[data-automation="job-detail-location"]',
                '[data-testid="job-location"]',
                '[data-automation="job-location"]',
                '[data-testid="location"]',
                '.location',
                '[class*="location"]',
                '.JobHeader-location',
            ],
            'description': [
                '[data-automation="jobAdDetails"]',
                '[data-automation="job-detail-description"]',
                '[data-testid="job-description"]',
                '[data-automation="jobDescription"]',
                '.job-description',
                '[class*="description"]',
                '.JobDetail-description',
                '.jobAdDetails',
            ],
            'requirements': [
                '[data-automation="job-requirements"]',
                '[data-testid="requirements"]',
                '.requirements',
                '.qualifications',
                '[class*="requirements"]',
                '[class*="qualifications"]',
            ]
        }
        
        # Update site config for SEEK
        self.site_configs['seek.com.au']['selectors'] = self.seek_selectors
    
    def scrape_seek_job(self, url: str) -> Tuple[Dict, str]:
        """SEEK-specific scraping with enhanced anti-detection"""
        
        logger.info(f"Starting SEEK-specific scraping for: {url}")
        
        try:
            # Use parent class anti-detection scraping
            job_data, method = self.scrape_protected_site(url)
            
            # SEEK-specific post-processing
            if job_data and not job_data.get('manual_entry_required'):
                job_data = self.enhance_seek_data(job_data)
            
            return job_data, f"seek_{method}"
            
        except Exception as e:
            logger.error(f"SEEK scraping failed: {str(e)}")
            return self.create_manual_fallback_response(url), f"seek_error_{str(e)}"
    
    def enhance_seek_data(self, job_data: Dict) -> Dict:
        """SEEK-specific data enhancement"""
        
        # Clean SEEK-specific artifacts
        seek_artifacts = [
            'SEEK', 'seek.com.au', 'Apply for this job',
            'Save this job', 'Email this job', 'Share this job',
            'Jobs in Australia', 'More jobs like this',
            'window.SEEK_REDUX_DATA', 'window.SEEK_CONFIG', 'window.SEEK_APOLLO_DATA'
        ]
        
        for field in ['title', 'company', 'description']:
            if job_data.get(field):
                # Remove SEEK artifacts
                for artifact in seek_artifacts:
                    job_data[field] = job_data[field].replace(artifact, '')
                
                # Additional JSON-encoded content cleaning for SEEK
                job_data[field] = self.remove_json_encoded_content(job_data[field])
                job_data[field] = job_data[field].strip()
        
        # Add SEEK-specific metadata
        job_data['site'] = 'SEEK'
        job_data['country'] = 'Australia'
        
        return job_data
