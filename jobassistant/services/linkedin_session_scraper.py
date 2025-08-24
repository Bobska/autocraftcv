"""
LinkedIn Session-Based Scraper for Authentication Bypass
"""

import time
import logging
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from selenium_stealth import stealth
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class LinkedInSessionScraper:
    """
    LinkedIn scraper that handles authentication and session management
    """
    
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.driver = None
        self.logged_in = False
        self.session_active = False
        
    def setup_driver(self, headless=False):
        """Setup undetected Chrome driver for LinkedIn"""
        if self.driver is not None:
            return True
            
        try:
            # Use undetected-chromedriver for better stealth
            options = uc.ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Persist session data - use temp directory for cross-platform compatibility
            temp_dir = tempfile.gettempdir()
            chrome_data_dir = os.path.join(temp_dir, 'chrome-linkedin-session')
            os.makedirs(chrome_data_dir, exist_ok=True)
            
            options.add_argument(f'--user-data-dir={chrome_data_dir}')
            options.add_argument('--profile-directory=LinkedIn')
            
            # Create undetected chrome instance
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Apply stealth techniques
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Set a realistic user agent
            ua = UserAgent()
            user_agent = ua.random
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            
            logger.info("LinkedIn session driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup LinkedIn session driver: {e}")
            return False
    
    def check_existing_session(self):
        """Check if there's an existing valid LinkedIn session"""
        try:
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(3)
            
            # Check if we're logged in by looking for feed content
            if 'feed' in self.driver.current_url or 'in/' in self.driver.current_url:
                # Look for user profile indicators
                profile_indicators = [
                    '[data-test-id="nav-user-image"]',
                    '.global-nav__me',
                    '[data-control-name="nav.settings_and_privacy"]'
                ]
                
                for indicator in profile_indicators:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, indicator)
                        self.logged_in = True
                        self.session_active = True
                        logger.info("Found existing LinkedIn session")
                        return True
                    except NoSuchElementException:
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking existing session: {e}")
            return False
    
    def login_to_linkedin(self):
        """Login to LinkedIn with provided credentials"""
        if not self.email or not self.password:
            logger.error("LinkedIn credentials not provided")
            return False
        
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Check for existing session first
            if self.check_existing_session():
                return True
            
            logger.info("Starting LinkedIn login process")
            
            # Go to LinkedIn login page
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            
            # Enter credentials
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            # Type slowly to avoid detection
            self.type_slowly(username_field, self.email)
            time.sleep(1)
            self.type_slowly(password_field, self.password)
            time.sleep(1)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            
            if 'feed' in current_url or 'in/' in current_url:
                self.logged_in = True
                self.session_active = True
                logger.info("LinkedIn login successful")
                return True
            elif 'challenge' in current_url or 'captcha' in current_url:
                # Handle challenges
                return self.handle_login_challenges()
            else:
                logger.error("LinkedIn login failed - unexpected redirect")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn login failed: {e}")
            return False
    
    def type_slowly(self, element, text):
        """Type text slowly to avoid detection"""
        for char in text:
            element.send_keys(char)
            time.sleep(0.1)  # Small delay between keystrokes
    
    def handle_login_challenges(self):
        """Handle 2FA, captcha, or security challenges"""
        try:
            logger.info("Handling LinkedIn login challenges")
            
            # Check for 2FA challenge
            if self.driver.find_elements(By.CSS_SELECTOR, '[data-test="challenge-form"]'):
                logger.info("2FA challenge detected")
                return self.handle_2fa_challenge()
                
            # Check for email verification
            elif 'checkpoint/challenge' in self.driver.current_url:
                logger.info("Email verification challenge detected")
                return self.handle_email_verification()
                
            # Check for captcha
            elif self.driver.find_elements(By.CSS_SELECTOR, '.captcha'):
                logger.info("Captcha challenge detected")
                return self.handle_captcha_challenge()
                
            # Wait a bit more and check again
            time.sleep(10)
            current_url = self.driver.current_url
            
            if 'feed' in current_url or 'in/' in current_url:
                self.logged_in = True
                self.session_active = True
                logger.info("Challenge resolved automatically")
                return True
            
            logger.warning("Unable to handle login challenge automatically")
            return False
            
        except Exception as e:
            logger.error(f"Error handling login challenges: {e}")
            return False
    
    def handle_2fa_challenge(self):
        """Handle 2FA challenge - requires manual intervention"""
        logger.info("2FA challenge requires manual intervention")
        
        # For now, we'll return False and recommend manual entry
        # In a full implementation, you might:
        # 1. Display a popup for user to enter 2FA code
        # 2. Use SMS API integration
        # 3. Wait for manual completion
        
        return False
    
    def handle_email_verification(self):
        """Handle email verification challenge"""
        logger.info("Email verification challenge - waiting for user action")
        
        # Wait up to 2 minutes for user to verify email
        for i in range(24):  # 24 * 5 seconds = 2 minutes
            time.sleep(5)
            current_url = self.driver.current_url
            
            if 'feed' in current_url or 'in/' in current_url:
                self.logged_in = True
                self.session_active = True
                logger.info("Email verification completed")
                return True
        
        logger.warning("Email verification timeout")
        return False
    
    def handle_captcha_challenge(self):
        """Handle captcha challenge"""
        logger.info("Captcha challenge detected - manual intervention may be required")
        
        # Wait for captcha to be solved (manually or automatically)
        for i in range(12):  # 12 * 5 seconds = 1 minute
            time.sleep(5)
            current_url = self.driver.current_url
            
            if 'feed' in current_url or 'in/' in current_url:
                self.logged_in = True
                self.session_active = True
                logger.info("Captcha challenge resolved")
                return True
        
        logger.warning("Captcha challenge timeout")
        return False
    
    def scrape_job_authenticated(self, job_url):
        """Scrape job posting with authenticated LinkedIn session"""
        if not self.logged_in:
            if not self.login_to_linkedin():
                logger.error("Cannot scrape job - LinkedIn login failed")
                return None
        
        try:
            logger.info(f"Scraping LinkedIn job with authentication: {job_url}")
            
            # Navigate to job posting
            self.driver.get(job_url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(5)  # Let dynamic content load
            
            # Check if we're still logged in
            if 'authwall' in self.driver.current_url or 'login' in self.driver.current_url:
                logger.warning("Session expired during job scraping")
                return None
            
            # Extract job details with full access
            job_data = self.extract_full_job_details()
            
            if job_data:
                logger.info("Successfully extracted LinkedIn job data with authentication")
                job_data['extraction_method'] = 'linkedin_authenticated'
                job_data['authentication_used'] = True
            
            return job_data
            
        except Exception as e:
            logger.error(f"Authenticated LinkedIn scraping failed: {e}")
            return None
    
    def extract_full_job_details(self):
        """Extract complete job details from authenticated LinkedIn page"""
        try:
            job_data = {}
            
            # Extract title
            job_data['title'] = self.extract_title()
            
            # Extract company
            job_data['company'] = self.extract_company()
            
            # Extract location
            job_data['location'] = self.extract_location()
            
            # Extract description
            job_data['description'] = self.extract_description()
            
            # Extract requirements
            job_data['requirements'] = self.extract_requirements()
            
            # Extract salary (if available)
            job_data['salary_range'] = self.extract_salary()
            
            # Extract employment type
            job_data['employment_type'] = self.extract_employment_type()
            
            # Extract application instructions
            job_data['application_instructions'] = self.extract_application_instructions()
            
            # Add metadata
            job_data['site_domain'] = 'linkedin.com'
            job_data['extraction_quality'] = 'high'
            job_data['needs_review'] = False
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return None
    
    def extract_title(self):
        """Extract job title"""
        selectors = [
            '.top-card-layout__title',
            'h1.t-24',
            '[data-test-id="job-title"]',
            '.jobs-unified-top-card__job-title',
            'h1'
        ]
        
        return self.extract_text_by_selectors(selectors, 'Job Title Not Available')
    
    def extract_company(self):
        """Extract company name"""
        selectors = [
            '.top-card-layout__card .top-card-layout__second-subline a',
            '.jobs-unified-top-card__company-name',
            '[data-test-id="job-company"]',
            '.top-card-layout__card .top-card-layout__second-subline',
            'a[data-control-name="job_details_topcard_company_url"]'
        ]
        
        return self.extract_text_by_selectors(selectors, 'Company Not Available')
    
    def extract_location(self):
        """Extract job location"""
        selectors = [
            '.top-card-layout__card .top-card-layout__third-subline',
            '.jobs-unified-top-card__bullet',
            '[data-test-id="job-location"]',
            '.top-card-layout__card .top-card-layout__second-subline span'
        ]
        
        location = self.extract_text_by_selectors(selectors, 'Location Not Available')
        
        # Clean and enhance location
        if location and location != 'Location Not Available':
            # Remove common LinkedIn location prefixes
            location = location.replace('Located in ', '').replace('Location: ', '')
            
            # Add Australia if it looks like an Australian location
            au_indicators = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT', 'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide']
            if any(indicator in location for indicator in au_indicators) and 'Australia' not in location:
                location += ', Australia'
        
        return location
    
    def extract_description(self):
        """Extract job description"""
        selectors = [
            '.jobs-description__content',
            '.jobs-box__content',
            '[data-test-id="job-description"]',
            '.jobs-description',
            '.description__text'
        ]
        
        description = self.extract_text_by_selectors(selectors, 'Job description not available')
        
        # Clean up description
        if description and description != 'Job description not available':
            # Remove "Show more" and similar UI elements
            description = description.replace('Show more', '').replace('Show less', '')
            description = description.replace('...', '').strip()
        
        return description
    
    def extract_requirements(self):
        """Extract job requirements"""
        # LinkedIn often includes requirements in the description
        # Try to find specific requirements sections
        selectors = [
            '.jobs-description__content',
            '.jobs-box__content'
        ]
        
        full_text = self.extract_text_by_selectors(selectors, '')
        
        if full_text:
            # Look for requirements sections
            requirements_keywords = ['requirements', 'qualifications', 'skills', 'experience', 'must have']
            
            lines = full_text.split('\n')
            requirements_section = []
            capture = False
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in requirements_keywords):
                    capture = True
                    requirements_section.append(line)
                elif capture and line:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        requirements_section.append(line)
                    elif len(line) > 20:  # Likely a requirement description
                        requirements_section.append(line)
                    else:
                        break  # End of requirements section
            
            if requirements_section:
                return '\n'.join(requirements_section)
        
        return ''
    
    def extract_salary(self):
        """Extract salary information"""
        selectors = [
            '.jobs-unified-top-card__job-insight',
            '.salary',
            '[data-test-id="salary"]'
        ]
        
        return self.extract_text_by_selectors(selectors, '')
    
    def extract_employment_type(self):
        """Extract employment type"""
        selectors = [
            '.jobs-unified-top-card__job-insight',
            '.employment-type',
            '[data-test-id="employment-type"]'
        ]
        
        return self.extract_text_by_selectors(selectors, '')
    
    def extract_application_instructions(self):
        """Extract application instructions"""
        selectors = [
            '.jobs-apply-button',
            '.apply-button',
            '[data-test-id="apply-button"]'
        ]
        
        # Check if there's an "Easy Apply" button or external application link
        try:
            easy_apply = self.driver.find_elements(By.CSS_SELECTOR, '.jobs-apply-button--top-card')
            if easy_apply:
                return "Apply directly through LinkedIn Easy Apply"
            
            external_apply = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-control-name="job_details_topcard_apply"]')
            if external_apply:
                return "Apply through company website (external link)"
                
        except:
            pass
        
        return ''
    
    def extract_text_by_selectors(self, selectors, default=''):
        """Extract text using multiple selectors as fallbacks"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    if text:
                        return text
            except:
                continue
        
        return default
    
    def cleanup(self):
        """Clean up driver resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("LinkedIn session driver cleanup completed")
            except:
                pass
            self.driver = None
            self.logged_in = False
            self.session_active = False
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
