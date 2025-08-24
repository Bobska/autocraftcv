"""
Enhanced LinkedIn Job Scraper
Specifically designed to handle LinkedIn's dynamic content and anti-scraping measures
"""

import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class LinkedInJobScraper:
    """Enhanced LinkedIn job scraper with anti-detection and comprehensive extraction"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configure undetected Chrome driver optimized for LinkedIn"""
        try:
            options = uc.ChromeOptions()
            
            # LinkedIn-optimized options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Faster loading
            options.add_argument('--disable-javascript')  # Try without JS first
            
            # LinkedIn-specific user agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f'--user-agent={user_agent}')
            
            # Additional stealth options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            self.driver = uc.Chrome(options=options)
            
            # Execute additional stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            logger.info("LinkedIn scraper driver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn driver: {str(e)}")
            # Fallback to regular Chrome
            self.setup_fallback_driver()
    
    def setup_fallback_driver(self):
        """Fallback to regular Chrome driver if undetected fails"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--headless')  # Run headless as fallback
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Fallback Chrome driver initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize fallback driver: {str(e)}")
            raise Exception("Could not initialize any Chrome driver")
    
    def scrape_linkedin_job(self, url: str) -> Tuple[Dict, str]:
        """Enhanced LinkedIn job scraping with comprehensive extraction"""
        try:
            logger.info(f"Starting LinkedIn scraping for: {url}")
            
            # Navigate to the job URL
            self.driver.get(url)
            
            # Wait for initial page load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Check for authentication wall
            if self.detect_auth_wall():
                logger.warning("LinkedIn authentication wall detected")
                return self.handle_auth_fallback(url)
            
            # Check for rate limiting or blocking
            if self.detect_rate_limiting():
                logger.warning("LinkedIn rate limiting detected")
                return self.handle_rate_limit_fallback(url)
            
            # Try to expand job description if there's a "Show more" button
            self.try_expand_description()
            
            # Extract all job data
            job_data = {
                'title': self.extract_linkedin_title(),
                'company': self.extract_linkedin_company(),
                'location': self.extract_linkedin_location(),
                'employment_type': self.extract_employment_type(),
                'salary_range': self.extract_salary_info(),
                'description': self.extract_job_description(),
                'requirements': self.extract_requirements(),
                'responsibilities': self.extract_responsibilities(),
                'application_instructions': self.extract_application_instructions(),
                'raw_content': self.get_page_text(),
                'url': url
            }
            
            # Validate extraction quality
            quality_score = self.assess_extraction_quality(job_data)
            
            if quality_score < 0.5:  # Poor extraction
                logger.warning(f"Poor extraction quality ({quality_score}), trying fallback")
                return self.fallback_extraction(url)
            
            logger.info(f"LinkedIn extraction successful (quality: {quality_score})")
            return job_data, 'linkedin_enhanced'
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {str(e)}")
            return self.fallback_extraction(url)
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def extract_linkedin_title(self) -> Optional[str]:
        """Extract job title with multiple LinkedIn selectors"""
        title_selectors = [
            'h1.top-card-layout__title',
            'h1[data-test-id="job-title"]',
            '.jobs-unified-top-card__job-title h1',
            '.job-details-jobs-unified-top-card__job-title h1',
            'h1.t-24.t-bold.jobs-unified-top-card__job-title',
            '.jobs-details__main-content h1',
            '.jobs-unified-top-card__job-title',
            'h1.jobs-top-card__job-title',
            '.job-details-top-card__job-title h1'
        ]
        
        for selector in title_selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                title = element.text.strip()
                if title and len(title) > 2:
                    logger.info(f"Found title with selector {selector}: {title}")
                    return title
            except:
                continue
        
        # Fallback: try to find title in page text
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            title_match = re.search(r'^([A-Z][^|\n]+?)\s*(?:\s+at\s+|\s*\|\s*)', page_text, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                logger.info(f"Found title via fallback: {title}")
                return title
        except:
            pass
        
        logger.warning("Could not extract job title")
        return None
    
    def extract_linkedin_company(self) -> Optional[str]:
        """Extract company name with LinkedIn-specific selectors"""
        company_selectors = [
            '.jobs-unified-top-card__company-name a',
            '.jobs-unified-top-card__company-name',
            'a[data-test-id="job-posting-company-name"]',
            '.jobs-details-top-card__company-info a',
            '.job-details-jobs-unified-top-card__company-name a',
            '.jobs-poster__name',
            '.jobs-unified-top-card__primary-description a',
            '.job-details-top-card__company-info .jobs-unified-top-card__company-name',
            '.jobs-top-card__company-name',
            '.hiring-team__name'
        ]
        
        for selector in company_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                company = element.text.strip()
                if company and len(company) > 1 and not company.lower() in ['follow', 'connect', 'message']:
                    logger.info(f"Found company with selector {selector}: {company}")
                    return company
            except:
                continue
        
        # Fallback: Look for company patterns in text
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Pattern 1: "at Company Name"
            company_match = re.search(r'\bat\s+([A-Z][^|\n•]+?)(?:\s*\||\s*•|\s*\n|\s*Location)', page_text)
            if company_match:
                company = company_match.group(1).strip()
                logger.info(f"Found company via 'at' pattern: {company}")
                return company
            
            # Pattern 2: Look for company name after job title
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if any(word in line.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'specialist']):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and len(next_line) > 2 and len(next_line) < 50:
                            logger.info(f"Found company via line pattern: {next_line}")
                            return next_line
            
        except:
            pass
        
        logger.warning("Could not extract company name")
        return None
    
    def extract_linkedin_location(self) -> Optional[str]:
        """Extract job location with comprehensive selectors"""
        location_selectors = [
            '.jobs-unified-top-card__bullet',
            '.jobs-unified-top-card__primary-description',
            'span[data-test-id="job-posting-location"]',
            '.jobs-details-top-card__bullet',
            '.jobs-unified-top-card__job-insight span',
            '.job-details-top-card__job-insight',
            '.jobs-top-card__bullet'
        ]
        
        # Try direct selectors first
        for selector in location_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if self.is_location_text(text):
                        logger.info(f"Found location with selector {selector}: {text}")
                        return text
            except:
                continue
        
        # Fallback: Search for location patterns in page text
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Australian location patterns
            au_location_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*,?\s*(?:NSW|QLD|VIC|WA|SA|TAS|ACT|NT|Queensland|New South Wales|Victoria|Western Australia|South Australia|Tasmania|Australian Capital Territory|Northern Territory|Australia))'
            
            location_match = re.search(au_location_pattern, page_text)
            if location_match:
                location = location_match.group(1).strip()
                logger.info(f"Found location via pattern: {location}")
                return location
            
            # General location patterns
            location_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # City, State/Country
                r'(Remote|Hybrid|On-site)',  # Work arrangement
                r'([A-Z][a-z]+\s+City)',  # City pattern
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, page_text)
                if match:
                    location = match.group(1).strip()
                    if self.is_location_text(location):
                        logger.info(f"Found location via pattern: {location}")
                        return location
                        
        except:
            pass
        
        logger.warning("Could not extract location")
        return None
    
    def extract_job_description(self) -> Optional[str]:
        """Extract full job description with comprehensive selectors"""
        description_selectors = [
            '.jobs-description-content__text',
            '.jobs-box__html-content',
            '.jobs-description',
            'div[data-test-id="job-description"]',
            '.jobs-description-details',
            '.job-details-jobs-unified-top-card__job-description',
            '.jobs-details__main-content .jobs-description',
            '.job-description-card__text'
        ]
        
        # Try each selector
        for selector in description_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                description_text = element.text.strip()
                
                if description_text and len(description_text) > 100:
                    logger.info(f"Found description with selector {selector} (length: {len(description_text)})")
                    return self.clean_description_text(description_text)
            except:
                continue
        
        # Fallback: Try to get the main content area
        try:
            main_content = self.driver.find_element(By.CSS_SELECTOR, '.jobs-details__main-content')
            description_text = main_content.text.strip()
            
            if description_text and len(description_text) > 100:
                logger.info(f"Found description via main content (length: {len(description_text)})")
                return self.clean_description_text(description_text)
        except:
            pass
        
        logger.warning("Could not extract job description")
        return None
    
    def extract_requirements(self) -> Optional[str]:
        """Extract requirements from job description"""
        description = self.extract_job_description()
        if not description:
            return None
        
        # Requirements section patterns
        requirements_patterns = [
            r"(?i)(?:requirements?|qualifications?|what you.ll need|you.ll ideally have|essential skills?|must have):?\s*\n?(.*?)(?=\n\s*(?:[A-Z][a-z]+\s*:|$|responsibilities|about|role|what we offer|benefits))",
            r"(?i)(?:we.re looking for|ideal candidate|you should have):?\s*\n?(.*?)(?=\n\s*(?:[A-Z][a-z]+\s*:|$|responsibilities|about|role))",
            r"(?i)(?:skills?|experience)(?:\s+(?:required|needed|wanted)):?\s*\n?(.*?)(?=\n\s*(?:[A-Z][a-z]+\s*:|$|responsibilities|about|role))"
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.DOTALL)
            if match:
                requirements = match.group(1).strip()
                if requirements and len(requirements) > 20:
                    # Clean up the requirements text
                    requirements = re.sub(r'\n+', '\n', requirements)
                    requirements = re.sub(r'^\s*[•·\-\*]\s*', '', requirements, flags=re.MULTILINE)
                    logger.info(f"Found requirements (length: {len(requirements)})")
                    return requirements
        
        # Fallback: Look for bullet points or numbered lists that might be requirements
        bullet_pattern = r"(?i)(?:[•·\-\*]\s*.{20,}(?:\n[•·\-\*]\s*.{10,})*)"
        bullet_matches = re.findall(bullet_pattern, description)
        
        if bullet_matches:
            # Find the longest bullet list (likely requirements)
            longest_match = max(bullet_matches, key=len)
            if len(longest_match) > 100:
                logger.info(f"Found requirements via bullet pattern (length: {len(longest_match)})")
                return longest_match.strip()
        
        logger.warning("Could not extract requirements")
        return None
    
    def extract_responsibilities(self) -> Optional[str]:
        """Extract responsibilities from job description"""
        description = self.extract_job_description()
        if not description:
            return None
        
        responsibilities_patterns = [
            r"(?i)(?:responsibilities|duties|role overview|what you.ll do|day to day|your role):?\s*\n?(.*?)(?=\n\s*(?:[A-Z][a-z]+\s*:|$|requirements|qualifications|skills|experience))",
            r"(?i)(?:you will|you.ll be|main duties):?\s*\n?(.*?)(?=\n\s*(?:[A-Z][a-z]+\s*:|$|requirements|qualifications))"
        ]
        
        for pattern in responsibilities_patterns:
            match = re.search(pattern, description, re.DOTALL)
            if match:
                responsibilities = match.group(1).strip()
                if responsibilities and len(responsibilities) > 20:
                    responsibilities = re.sub(r'\n+', '\n', responsibilities)
                    logger.info(f"Found responsibilities (length: {len(responsibilities)})")
                    return responsibilities
        
        logger.warning("Could not extract responsibilities")
        return None
    
    def extract_salary_info(self) -> Optional[str]:
        """Extract salary information"""
        salary_selectors = [
            '.jobs-unified-top-card__job-insight',
            '.jobs-details-top-card__job-insight',
            '.job-details-top-card__job-insight',
            '.jobs-unified-top-card__job-insight-text'
        ]
        
        # Try direct selectors
        for selector in salary_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if self.is_salary_text(text):
                        logger.info(f"Found salary with selector {selector}: {text}")
                        return text
            except:
                continue
        
        # Fallback: Search page text for salary patterns
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Australian salary patterns
            salary_patterns = [
                r'A?\$[\d,]+(?:\.?\d{2})?\s*(?:-|to)\s*A?\$[\d,]+(?:\.?\d{2})?\s*(?:per\s+|/)(?:year|yr|annum)',
                r'A?\$[\d,]+(?:\.?\d{2})?(?:\s*k)?\s*(?:-|to)\s*A?\$[\d,]+(?:\.?\d{2})?(?:\s*k)?\s*(?:per\s+|/)(?:year|yr)',
                r'A?\$[\d,]+(?:\.?\d{2})?\s*(?:per\s+|/)(?:year|yr|annum)',
                r'[\d,]+k?\s*(?:-|to)\s*[\d,]+k?\s*(?:per\s+year|annually)'
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    salary = match.group(0).strip()
                    logger.info(f"Found salary via pattern: {salary}")
                    return salary
                    
        except:
            pass
        
        logger.warning("Could not extract salary information")
        return None
    
    def extract_employment_type(self) -> Optional[str]:
        """Extract employment type (Full-time, Part-time, etc.)"""
        type_selectors = [
            '.jobs-unified-top-card__job-insight',
            '.jobs-details-top-card__job-insight',
            '.job-details-top-card__job-insight'
        ]
        
        employment_types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'casual', 'permanent']
        
        # Try direct selectors
        for selector in type_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip().lower()
                    for emp_type in employment_types:
                        if emp_type in text:
                            logger.info(f"Found employment type: {text.title()}")
                            return text.title()
            except:
                continue
        
        # Fallback: Search page text
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            for emp_type in employment_types:
                if emp_type in page_text:
                    logger.info(f"Found employment type via text search: {emp_type.title()}")
                    return emp_type.title()
        except:
            pass
        
        logger.warning("Could not extract employment type")
        return None
    
    def extract_application_instructions(self) -> Optional[str]:
        """Extract special application instructions"""
        description = self.extract_job_description()
        if not description:
            return None
        
        # Look for email or special application instructions
        email_pattern = r'(?i)(?:email|send|contact).*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        email_match = re.search(email_pattern, description)
        
        if email_match:
            # Extract surrounding context for instructions
            email_pos = email_match.start()
            context_start = max(0, email_pos - 200)
            context_end = min(len(description), email_pos + 300)
            context = description[context_start:context_end]
            
            logger.info("Found application instructions with email")
            return f"Special application instructions: {context.strip()}"
        
        # Look for other application instructions
        instruction_patterns = [
            r"(?i)(?:to apply|application process|how to apply):?\s*\n?(.*?)(?=\n\s*[A-Z]|\n\s*$)",
            r"(?i)(?:please|kindly).*?(?:apply|send|submit).*?(?:to|at|via).*",
        ]
        
        for pattern in instruction_patterns:
            match = re.search(pattern, description, re.DOTALL)
            if match:
                instructions = match.group(0).strip()
                if len(instructions) > 20:
                    logger.info("Found application instructions")
                    return instructions
        
        return None
    
    def try_expand_description(self):
        """Try to click 'Show more' button to expand job description"""
        show_more_selectors = [
            '[data-test-id="job-description-show-more-button"]',
            '.jobs-description__footer button',
            'button:contains("Show more")',
            '.jobs-description-details button',
            '.see-more'
        ]
        
        for selector in show_more_selectors:
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, selector)
                if show_more.is_displayed():
                    show_more.click()
                    time.sleep(2)
                    logger.info("Expanded job description")
                    return
            except:
                continue
    
    def detect_auth_wall(self) -> bool:
        """Check if LinkedIn is requiring login"""
        auth_indicators = [
            'sign in',
            'join now',
            'authentication',
            'login required',
            'member login',
            'sign up'
        ]
        
        try:
            page_source = self.driver.page_source.lower()
            return any(indicator in page_source for indicator in auth_indicators)
        except:
            return False
    
    def detect_rate_limiting(self) -> bool:
        """Check if LinkedIn is rate limiting or blocking"""
        blocking_indicators = [
            'too many requests',
            'rate limit',
            'try again later',
            'blocked',
            'suspicious activity'
        ]
        
        try:
            page_source = self.driver.page_source.lower()
            return any(indicator in page_source for indicator in blocking_indicators)
        except:
            return False
    
    def is_location_text(self, text: str) -> bool:
        """Check if text looks like a location"""
        if not text or len(text) > 100:  # Too long to be a location
            return False
            
        location_indicators = [
            # Australian locations
            'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'canberra',
            'queensland', 'nsw', 'vic', 'wa', 'sa', 'tas', 'act', 'nt',
            'new south wales', 'victoria', 'western australia', 'south australia',
            'tasmania', 'northern territory', 'australian capital territory',
            
            # Work arrangements
            'remote', 'hybrid', 'on-site', 'onsite', 'work from home',
            
            # General location indicators
            'city', 'suburb', 'metro', 'cbd', 'downtown'
        ]
        
        text_lower = text.lower()
        
        # Check for location indicators
        has_location_indicator = any(indicator in text_lower for indicator in location_indicators)
        
        # Check for location patterns (City, State format)
        has_location_pattern = bool(re.search(r'[A-Z][a-z]+,\s*[A-Z]', text))
        
        # Exclude common non-location words
        exclude_words = ['follow', 'connect', 'message', 'apply', 'view', 'save', 'share']
        has_exclude_words = any(word in text_lower for word in exclude_words)
        
        return (has_location_indicator or has_location_pattern) and not has_exclude_words
    
    def is_salary_text(self, text: str) -> bool:
        """Check if text contains salary information"""
        if not text:
            return False
            
        salary_indicators = ['$', 'dollar', 'salary', 'pay', 'wage', 'compensation', 'remuneration']
        time_indicators = ['year', 'yr', 'annual', 'annum', 'hour', 'hr', 'week']
        
        text_lower = text.lower()
        has_salary = any(indicator in text_lower for indicator in salary_indicators)
        has_time = any(indicator in text_lower for indicator in time_indicators)
        
        return has_salary and (has_time or '$' in text)
    
    def clean_description_text(self, text: str) -> str:
        """Clean and format job description text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove common LinkedIn UI elements
        ui_elements = [
            'Show more', 'Show less', 'See more', 'See less',
            'Follow', 'Connect', 'Message', 'Save', 'Report job',
            'Easy Apply', 'Apply now', 'Apply on company website'
        ]
        
        for element in ui_elements:
            text = text.replace(element, '')
        
        return text.strip()
    
    def assess_extraction_quality(self, job_data: Dict) -> float:
        """Assess the quality of extracted job data"""
        score = 0.0
        total_fields = 6  # title, company, location, description, requirements, salary
        
        # Title (required)
        if job_data.get('title') and len(job_data['title']) > 2:
            score += 1.5  # Title is most important
        
        # Company (required)  
        if job_data.get('company') and len(job_data['company']) > 1:
            score += 1.5  # Company is very important
        
        # Location
        if job_data.get('location') and len(job_data['location']) > 2:
            score += 1.0
        
        # Description
        if job_data.get('description') and len(job_data['description']) > 100:
            score += 1.0
        
        # Requirements
        if job_data.get('requirements') and len(job_data['requirements']) > 20:
            score += 0.5
        
        # Salary
        if job_data.get('salary_range'):
            score += 0.5
        
        return score / total_fields
    
    def get_page_text(self) -> str:
        """Get all text content from the page"""
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            return body.text
        except:
            return ""
    
    def handle_auth_fallback(self, url: str) -> Tuple[Dict, str]:
        """Handle cases where LinkedIn requires authentication"""
        fallback_data = {
            'title': 'Authentication Required',
            'company': 'LinkedIn Login Required',
            'location': None,
            'description': f'LinkedIn requires login to view this job posting: {url}',
            'requirements': None,
            'responsibilities': None,
            'salary_range': None,
            'employment_type': None,
            'application_instructions': None,
            'raw_content': 'LinkedIn authentication wall detected',
            'requires_manual_entry': True,
            'fallback_message': 'Please copy and paste the job content manually or try accessing the URL in a regular browser.',
            'url': url
        }
        
        logger.warning(f"LinkedIn authentication required for: {url}")
        return fallback_data, 'linkedin_auth_required'
    
    def handle_rate_limit_fallback(self, url: str) -> Tuple[Dict, str]:
        """Handle cases where LinkedIn is rate limiting"""
        fallback_data = {
            'title': 'Rate Limited',
            'company': 'LinkedIn Rate Limited',
            'location': None,
            'description': f'LinkedIn is rate limiting requests. Please try again later: {url}',
            'requirements': None,
            'responsibilities': None,
            'salary_range': None,
            'employment_type': None,
            'application_instructions': None,
            'raw_content': 'LinkedIn rate limiting detected',
            'requires_manual_entry': True,
            'fallback_message': 'LinkedIn is blocking automated requests. Please try again later or use manual entry.',
            'url': url
        }
        
        logger.warning(f"LinkedIn rate limiting detected for: {url}")
        return fallback_data, 'linkedin_rate_limited'
    
    def fallback_extraction(self, url: str) -> Tuple[Dict, str]:
        """Fallback extraction when normal methods fail"""
        try:
            logger.info("Attempting fallback extraction")
            
            # Try to get any visible text
            page_text = self.get_page_text()
            
            if not page_text:
                return self.create_failed_extraction(url)
            
            # Basic pattern matching for job info
            title = None
            company = None
            location = None
            
            # Extract title (first substantial line)
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            for line in lines:
                if len(line) > 5 and len(line) < 100 and not any(word in line.lower() for word in ['follow', 'connect', 'linkedin']):
                    title = line
                    break
            
            # Extract company (look for "at Company" pattern)
            company_match = re.search(r'\bat\s+([A-Z][^|\n•]+?)(?:\s*\||\s*•|\s*\n)', page_text)
            if company_match:
                company = company_match.group(1).strip()
            
            # Extract location (Australian patterns)
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s*(?:NSW|QLD|VIC|WA|SA|TAS|ACT|NT|Queensland|New South Wales|Victoria|Australia))', page_text)
            if location_match:
                location = location_match.group(1).strip()
            
            # Extract salary
            salary_match = re.search(r'A?\$[\d,]+(?:\.?\d{2})?\s*(?:-|to)\s*A?\$[\d,]+(?:\.?\d{2})?\s*(?:per\s+|/)(?:year|yr)', page_text)
            salary = salary_match.group(0).strip() if salary_match else None
            
            fallback_data = {
                'title': title or 'Title Extraction Failed',
                'company': company or 'Company Extraction Failed',
                'location': location,
                'description': page_text[:1000] if page_text else None,
                'requirements': None,
                'responsibilities': None,
                'salary_range': salary,
                'employment_type': None,
                'application_instructions': None,
                'raw_content': page_text,
                'requires_manual_entry': True,
                'extraction_method': 'fallback',
                'url': url
            }
            
            logger.info(f"Fallback extraction completed: title={title}, company={company}")
            return fallback_data, 'linkedin_fallback'
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {str(e)}")
            return self.create_failed_extraction(url)
    
    def create_failed_extraction(self, url: str) -> Tuple[Dict, str]:
        """Create a failed extraction result"""
        failed_data = {
            'title': 'Extraction Failed',
            'company': 'Extraction Failed',
            'location': None,
            'description': f'Could not extract content from LinkedIn URL: {url}',
            'requirements': None,
            'responsibilities': None,
            'salary_range': None,
            'employment_type': None,
            'application_instructions': None,
            'raw_content': 'Extraction completely failed',
            'requires_manual_entry': True,
            'extraction_method': 'failed',
            'url': url
        }
        
        logger.error(f"Complete extraction failure for: {url}")
        return failed_data, 'linkedin_failed'
