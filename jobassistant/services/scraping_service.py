"""
Enhanced Job scraping service with multiple strategies and anti-detection capabilities
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import re
from typing import Dict, Optional, Tuple
from django.conf import settings
import logging
from .enhanced_scraping_service import EnhancedJobScrapingService
from .anti_detection_scraper import AntiDetectionScraper, SEEKSpecificScraper

logger = logging.getLogger(__name__)


class JobScrapingService:
    """Enhanced service for scraping job postings from various websites with anti-detection"""
    
    def __init__(self, use_paid_apis: bool = False):
        self.use_paid_apis = use_paid_apis
        self.enhanced_scraper = EnhancedJobScrapingService()
        self.anti_detection_scraper = AntiDetectionScraper()
        self.seek_scraper = SEEKSpecificScraper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_job(self, url: str) -> Tuple[Dict, str]:
        """
        Main method to scrape job posting from URL using multi-tier approach
        Returns: (job_data_dict, method_used)
        """
        logger.info(f"Starting comprehensive job scraping for URL: {url}")
        
        # Tier 1: Try enhanced scraper first (fastest)
        try:
            job_data, method = self.enhanced_scraper.scrape_job(url)
            if self._validate_job_data(job_data):
                logger.info(f"Successfully scraped with enhanced scraper ({method})")
                return job_data, f"enhanced_{method}"
            else:
                logger.info("Enhanced scraper returned insufficient data, trying anti-detection methods")
        except Exception as e:
            logger.warning(f"Enhanced scraper failed: {str(e)}, trying anti-detection methods")
        
        # Tier 2: Try anti-detection scraper for protected sites
        try:
            if self._needs_anti_detection(url):
                logger.info("Using anti-detection scraping for protected site")
                
                if 'seek.com' in url.lower():
                    job_data, method = self.seek_scraper.scrape_seek_job(url)
                else:
                    job_data, method = self.anti_detection_scraper.scrape_protected_site(url)
                
                # Check if manual entry is required
                if job_data.get('manual_entry_required') or job_data.get('requires_manual_fallback'):
                    logger.warning("Anti-detection scraper requires manual fallback")
                    return job_data, method
                
                if self._validate_job_data(job_data):
                    logger.info(f"Successfully scraped with anti-detection ({method})")
                    return job_data, f"anti_detection_{method}"
                else:
                    logger.warning("Anti-detection scraper returned insufficient data")
            
        except Exception as e:
            logger.warning(f"Anti-detection scraper failed: {str(e)}, trying fallback methods")
        
        # Tier 3: Fallback to original strategies if needed
        try:
            if self.use_paid_apis:
                job_data, method = self._scrape_with_paid_apis(url)
                if self._validate_job_data(job_data):
                    return job_data, method
            else:
                job_data, method = self._scrape_with_free_tools(url)
                if self._validate_job_data(job_data):
                    return job_data, method
        except Exception as e:
            logger.warning(f"Fallback scraping failed: {str(e)}")
        
        # Final fallback - return manual entry required
        logger.warning("All scraping methods failed, returning manual entry requirement")
        return self._get_manual_entry_fallback(url), "manual_entry_required"
    
    def _needs_anti_detection(self, url: str) -> bool:
        """Determine if URL likely needs anti-detection methods"""
        protected_sites = [
            'seek.com',
            'linkedin.com',
            'glassdoor.com',
            'indeed.com',
            'monster.com',
            'ziprecruiter.com'
        ]
        
        url_lower = url.lower()
        return any(site in url_lower for site in protected_sites)
    
    def _validate_job_data(self, job_data: Dict) -> bool:
        """Validate that we have meaningful job data"""
        if not job_data:
            return False
        
        # Check for manual entry requirements
        if job_data.get('manual_entry_required') or job_data.get('requires_manual_fallback'):
            return False
        
        # Check for meaningful title and company
        title = job_data.get('title', '').strip()
        company = job_data.get('company', '').strip()
        
        # Must have either a meaningful title or company name
        has_title = (title and 
                    len(title) > 5 and 
                    'not available' not in title.lower() and 
                    'extraction failed' not in title.lower() and
                    'manual entry required' not in title.lower() and
                    'manual review required' not in title.lower())
        
        has_company = (company and 
                      len(company) > 2 and 
                      'not available' not in company.lower() and 
                      'unknown' not in company.lower() and
                      'extraction failed' not in company.lower() and
                      'manual entry required' not in company.lower() and
                      'manual review required' not in company.lower())
        
        return has_title or has_company
    
    def _get_manual_entry_fallback(self, url: str) -> Dict:
        """Create fallback data indicating manual entry is required"""
        return {
            'title': 'Manual Entry Required - Automatic Extraction Failed',
            'company': 'Manual Entry Required - Automatic Extraction Failed',
            'description': f'All automatic scraping methods failed for URL: {url}. This may be due to anti-bot protection, site changes, or complex page structure. Please use manual entry to paste the job content.',
            'location': 'Manual Entry Required',
            'requirements': 'Manual Entry Required',
            'responsibilities': 'Manual Entry Required',
            'salary_range': '',
            'employment_type': '',
            'url': url,
            'extraction_status': 'manual_required',
            'manual_entry_required': True,
            'requires_manual_fallback': True,
            'all_methods_failed': True,
            'suggested_action': 'manual_entry'
        }
    
    def _scrape_with_paid_apis(self, url: str) -> Tuple[Dict, str]:
        """Scrape using paid APIs like ScrapingBee or Diffbot"""
        
        # Try ScrapingBee first
        scrapingbee_key = getattr(settings, 'SCRAPINGBEE_API_KEY', None)
        if scrapingbee_key:
            try:
                job_data = self._scrape_with_scrapingbee(url, scrapingbee_key)
                if job_data:
                    return job_data, "scrapingbee"
            except Exception as e:
                logger.warning(f"ScrapingBee failed: {e}")
        
        # Try Diffbot
        diffbot_key = getattr(settings, 'DIFFBOT_API_KEY', None)
        if diffbot_key:
            try:
                job_data = self._scrape_with_diffbot(url, diffbot_key)
                if job_data:
                    return job_data, "diffbot"
            except Exception as e:
                logger.warning(f"Diffbot failed: {e}")
        
        # Fallback to free tools
        return self._scrape_with_free_tools(url)
    
    def _scrape_with_scrapingbee(self, url: str, api_key: str) -> Dict:
        """Scrape using ScrapingBee API"""
        api_url = "https://app.scrapingbee.com/api/v1/"
        params = {
            'api_key': api_key,
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true'
        }
        
        response = self.session.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return self._parse_job_content(soup, url)
    
    def _scrape_with_diffbot(self, url: str, api_key: str) -> Dict:
        """Scrape using Diffbot API"""
        api_url = f"https://api.diffbot.com/v3/article?token={api_key}&url={url}"
        
        response = self.session.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'objects' in data and data['objects']:
            article = data['objects'][0]
            return {
                'title': article.get('title', ''),
                'company': self._extract_company_from_text(article.get('text', '')),
                'description': article.get('text', ''),
                'raw_content': article.get('html', ''),
                'requirements': self._extract_requirements_from_text(article.get('text', '')),
                'responsibilities': self._extract_responsibilities_from_text(article.get('text', '')),
            }
        
        return {}
    
    def _scrape_with_free_tools(self, url: str) -> Tuple[Dict, str]:
        """Scrape using free tools (requests + BeautifulSoup, Selenium)"""
        
        # Try simple requests first
        try:
            job_data = self._scrape_with_requests(url)
            if job_data and job_data.get('title'):
                return job_data, "beautifulsoup"
        except Exception as e:
            logger.warning(f"BeautifulSoup scraping failed: {e}")
        
        # Try Selenium for JavaScript-heavy sites
        try:
            job_data = self._scrape_with_selenium(url)
            if job_data and job_data.get('title'):
                return job_data, "selenium"
        except Exception as e:
            logger.warning(f"Selenium scraping failed: {e}")
        
        return {}, "failed"
    
    def _scrape_with_requests(self, url: str) -> Dict:
        """Scrape using requests and BeautifulSoup"""
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return self._parse_job_content(soup, url)
    
    def _scrape_with_selenium(self, url: str) -> Dict:
        """Scrape using Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return self._parse_job_content(soup, url)
            
        finally:
            if driver:
                driver.quit()
    
    def _parse_job_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Parse job content from BeautifulSoup object"""
        
        # Determine site type and use appropriate parser
        if 'linkedin.com' in url:
            return self._parse_linkedin_job(soup)
        elif 'indeed.com' in url:
            return self._parse_indeed_job(soup)
        elif 'glassdoor.com' in url:
            return self._parse_glassdoor_job(soup)
        else:
            return self._parse_generic_job(soup)
    
    def _parse_linkedin_job(self, soup: BeautifulSoup) -> Dict:
        """Parse LinkedIn job posting"""
        job_data = {}
        
        # Title
        title_selectors = [
            'h1.t-24.t-bold.inline',
            'h1[data-automation-id="jobPostingHeader"]',
            '.job-details-jobs-unified-top-card__job-title',
            'h1.job-title'
        ]
        job_data['title'] = self._extract_text_by_selectors(soup, title_selectors)
        
        # Company
        company_selectors = [
            '.job-details-jobs-unified-top-card__company-name',
            '.jobs-unified-top-card__company-name',
            'a[data-automation-id="jobPostingCompanyLink"]',
            '.company-name'
        ]
        job_data['company'] = self._extract_text_by_selectors(soup, company_selectors)
        
        # Location
        location_selectors = [
            '.job-details-jobs-unified-top-card__bullet',
            '.jobs-unified-top-card__bullet',
            '[data-automation-id="jobPostingLocation"]'
        ]
        job_data['location'] = self._extract_text_by_selectors(soup, location_selectors)
        
        # Description
        description_selectors = [
            '.jobs-description-content__text',
            '.jobs-box__html-content',
            '.description-content'
        ]
        job_data['description'] = self._extract_text_by_selectors(soup, description_selectors)
        
        return self._extract_additional_info(job_data, soup)
    
    def _parse_indeed_job(self, soup: BeautifulSoup) -> Dict:
        """Parse Indeed job posting"""
        job_data = {}
        
        # Title
        title_selectors = [
            'h1[data-testid="jobsearch-JobInfoHeader-title"]',
            'h1.jobsearch-JobInfoHeader-title',
            '.jobsearch-JobInfoHeader-title'
        ]
        job_data['title'] = self._extract_text_by_selectors(soup, title_selectors)
        
        # Company
        company_selectors = [
            '[data-testid="inlineHeader-companyName"]',
            '.jobsearch-InlineCompanyRating',
            '.jobsearch-JobInfoHeader-subtitle'
        ]
        job_data['company'] = self._extract_text_by_selectors(soup, company_selectors)
        
        # Location
        location_selectors = [
            '[data-testid="job-location"]',
            '.jobsearch-JobInfoHeader-subtitle'
        ]
        job_data['location'] = self._extract_text_by_selectors(soup, location_selectors)
        
        # Description
        description_selectors = [
            '#jobDescriptionText',
            '.jobsearch-jobDescriptionText',
            '.job-description'
        ]
        job_data['description'] = self._extract_text_by_selectors(soup, description_selectors)
        
        return self._extract_additional_info(job_data, soup)
    
    def _parse_glassdoor_job(self, soup: BeautifulSoup) -> Dict:
        """Parse Glassdoor job posting"""
        job_data = {}
        
        # Title
        title_selectors = [
            '[data-test="job-title"]',
            '.jobTitle',
            'h1'
        ]
        job_data['title'] = self._extract_text_by_selectors(soup, title_selectors)
        
        # Company
        company_selectors = [
            '[data-test="employer-name"]',
            '.employerName',
            '.company'
        ]
        job_data['company'] = self._extract_text_by_selectors(soup, company_selectors)
        
        # Location
        location_selectors = [
            '[data-test="job-location"]',
            '.location'
        ]
        job_data['location'] = self._extract_text_by_selectors(soup, location_selectors)
        
        # Description
        description_selectors = [
            '[data-test="jobDescriptionContent"]',
            '.jobDescriptionContent',
            '.job-description'
        ]
        job_data['description'] = self._extract_text_by_selectors(soup, description_selectors)
        
        return self._extract_additional_info(job_data, soup)
    
    def _parse_generic_job(self, soup: BeautifulSoup) -> Dict:
        """Parse generic job posting using common patterns"""
        job_data = {}
        
        # Title - look for h1 or elements with job/title keywords
        title_selectors = [
            'h1',
            '[class*="title"]',
            '[class*="job-title"]',
            '[id*="title"]',
            '[id*="job-title"]'
        ]
        job_data['title'] = self._extract_text_by_selectors(soup, title_selectors)
        
        # Company - look for elements with company keywords
        company_selectors = [
            '[class*="company"]',
            '[id*="company"]',
            '[class*="employer"]',
            '[id*="employer"]'
        ]
        job_data['company'] = self._extract_text_by_selectors(soup, company_selectors)
        
        # Location
        location_selectors = [
            '[class*="location"]',
            '[id*="location"]',
            '[class*="address"]'
        ]
        job_data['location'] = self._extract_text_by_selectors(soup, location_selectors)
        
        # Description - look for large text blocks
        description_selectors = [
            '[class*="description"]',
            '[id*="description"]',
            '[class*="content"]',
            '.job-content',
            'main',
            'article'
        ]
        job_data['description'] = self._extract_text_by_selectors(soup, description_selectors)
        
        return self._extract_additional_info(job_data, soup)
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: list) -> str:
        """Extract text using a list of CSS selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return ""
    
    def _extract_additional_info(self, job_data: Dict, soup: BeautifulSoup) -> Dict:
        """Extract additional information like requirements, responsibilities, etc."""
        
        full_text = soup.get_text()
        job_data['raw_content'] = str(soup)
        
        # Extract requirements
        job_data['requirements'] = self._extract_requirements_from_text(full_text)
        
        # Extract responsibilities
        job_data['responsibilities'] = self._extract_responsibilities_from_text(full_text)
        
        # Extract qualifications
        job_data['qualifications'] = self._extract_qualifications_from_text(full_text)
        
        # Extract salary if available
        job_data['salary_range'] = self._extract_salary_from_text(full_text)
        
        # Extract employment type
        job_data['employment_type'] = self._extract_employment_type_from_text(full_text)
        
        return job_data
    
    def _extract_requirements_from_text(self, text: str) -> str:
        """Extract requirements section from text"""
        patterns = [
            r'(?:requirements?|required|must have)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:qualifications?)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:skills?)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_responsibilities_from_text(self, text: str) -> str:
        """Extract responsibilities section from text"""
        patterns = [
            r'(?:responsibilities|duties|role)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:you will|what you.ll do)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_qualifications_from_text(self, text: str) -> str:
        """Extract qualifications section from text"""
        patterns = [
            r'(?:qualifications?|preferred|nice to have)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)',
            r'(?:education|degree)[:\n]([^§]*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_salary_from_text(self, text: str) -> str:
        """Extract salary information from text"""
        patterns = [
            r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per|\/)\s*(?:year|hour|month))?',
            r'[\d,]+k?\s*-\s*[\d,]+k?\s*(?:per|\/)\s*(?:year|annum)',
            r'(?:salary|compensation)[:\s]*\$?[\d,]+(?:\s*-\s*\$?[\d,]+)?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_employment_type_from_text(self, text: str) -> str:
        """Extract employment type from text"""
        types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance']
        
        for emp_type in types:
            if re.search(r'\b' + emp_type + r'\b', text, re.IGNORECASE):
                return emp_type.title()
        
        return ""
    
    def _extract_company_from_text(self, text: str) -> str:
        """Extract company name from text using patterns"""
        # This is a simplified version - in practice, you'd use more sophisticated NLP
        lines = text.split('\n')[:5]  # Check first few lines
        
        for line in lines:
            if re.search(r'\b(inc|corp|ltd|llc|company|solutions|technologies)\b', line, re.IGNORECASE):
                return line.strip()
        
        return ""
