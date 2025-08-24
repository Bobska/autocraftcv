"""
Enhanced Job Scraping Service with Multiple Strategies and Robust Error Handling
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
import random
from typing import Dict, Optional, Tuple, List
from django.conf import settings
import logging
from urllib.parse import urlparse, urljoin
import html

logger = logging.getLogger(__name__)


class EnhancedJobScrapingService:
    """Enhanced job scraping service with multiple strategies and robust error handling"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
        # Scraping strategies in order of preference
        self.strategies = [
            self._scrape_structured_data,
            self._scrape_with_enhanced_selectors,
            self._scrape_with_content_analysis,
            self._scrape_with_text_mining
        ]
    
    def setup_session(self):
        """Setup session with realistic headers and settings"""
        # Rotate user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def scrape_job(self, url: str) -> Tuple[Dict, str]:
        """
        Main scraping method that tries multiple strategies
        Returns: (job_data_dict, method_used)
        """
        logger.info(f"Starting job scraping for URL: {url}")
        
        # Validate URL
        if not self._is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return self._create_fallback_result(url, "Invalid URL"), "error"
        
        # Get page content
        try:
            soup, response = self._fetch_page_content(url)
            if not soup:
                return self._create_fallback_result(url, "Failed to fetch content"), "error"
            
            logger.info(f"Successfully fetched content. Page size: {len(response.content)} bytes")
            
        except Exception as e:
            logger.error(f"Failed to fetch page: {str(e)}")
            return self._create_fallback_result(url, f"Fetch error: {str(e)}"), "error"
        
        # Try each scraping strategy
        for i, strategy in enumerate(self.strategies, 1):
            try:
                logger.info(f"Trying strategy {i}: {strategy.__name__}")
                job_data = strategy(soup, url)
                
                if self._is_valid_extraction(job_data):
                    method_name = strategy.__name__.replace('_scrape_', '')
                    logger.info(f"Success with strategy: {method_name}")
                    logger.info(f"Extracted - Title: {job_data.get('title', 'N/A')[:50]}, Company: {job_data.get('company', 'N/A')}")
                    return job_data, method_name
                else:
                    logger.warning(f"Strategy {strategy.__name__} returned insufficient data")
                    
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        # All strategies failed - create a fallback result with raw content for manual review
        logger.warning("All scraping strategies failed, creating fallback result")
        fallback_result = self._create_intelligent_fallback(soup, url)
        return fallback_result, "fallback"
    
    def _fetch_page_content(self, url: str) -> Tuple[Optional[BeautifulSoup], Optional[requests.Response]]:
        """Fetch page content with retry logic and error handling"""
        
        for attempt in range(3):  # 3 retry attempts
            try:
                logger.info(f"Fetching URL (attempt {attempt + 1}): {url}")
                
                # Add delay to avoid rate limiting
                if attempt > 0:
                    time.sleep(2)
                
                response = self.session.get(url, timeout=30, allow_redirects=True)
                
                # Check if we got redirected to an error page
                if response.url != url and any(error_term in response.url.lower() for error_term in ['error', '404', 'not-found', 'blocked']):
                    logger.warning(f"Redirected to error page: {response.url}")
                    continue
                
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    logger.warning(f"Unexpected content type: {content_type}")
                    continue
                
                # Check content length
                if len(response.content) < 1000:
                    logger.warning(f"Content too short: {len(response.content)} bytes")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Basic validation - page should have some content
                if not soup.find('body') or len(soup.get_text().strip()) < 100:
                    logger.warning("Page appears to be empty or blocked")
                    continue
                
                return soup, response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == 2:  # Last attempt
                    raise
                continue
        
        return None, None
    
    def _scrape_structured_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract job data from structured data (JSON-LD, microdata, etc.)"""
        job_data = {}
        
        # Look for JSON-LD structured data
        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for JobPosting schema
                if data.get('@type') == 'JobPosting' or (isinstance(data.get('@type'), list) and 'JobPosting' in data.get('@type', [])):
                    job_data.update({
                        'title': data.get('title', ''),
                        'company': self._extract_company_from_structured_data(data),
                        'description': data.get('description', ''),
                        'location': self._extract_location_from_structured_data(data),
                        'employment_type': data.get('employmentType', ''),
                        'salary_range': self._extract_salary_from_structured_data(data),
                        'date_posted': data.get('datePosted', ''),
                    })
                    
                    if job_data['title'] and job_data['company']:
                        logger.info("Successfully extracted from JSON-LD structured data")
                        return self._enhance_job_data(job_data, soup)
                        
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
                continue
        
        # Look for microdata
        microdata = self._extract_microdata(soup)
        if microdata.get('title') and microdata.get('company'):
            return self._enhance_job_data(microdata, soup)
        
        return {}
    
    def _scrape_with_enhanced_selectors(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape using enhanced CSS selectors based on site patterns"""
        
        # Detect job site and use specific selectors
        site_type = self._detect_job_site(url)
        
        if site_type == 'linkedin':
            return self._scrape_linkedin_enhanced(soup)
        elif site_type == 'indeed':
            return self._scrape_indeed_enhanced(soup)
        elif site_type == 'glassdoor':
            return self._scrape_glassdoor_enhanced(soup)
        else:
            return self._scrape_generic_enhanced(soup)
    
    def _scrape_with_content_analysis(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape using content analysis and pattern matching"""
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'menu']):
            element.decompose()
        
        # Get all text content
        text_content = soup.get_text()
        
        job_data = {
            'title': self._extract_title_from_text(text_content, soup),
            'company': self._extract_company_from_text(text_content, soup),
            'location': self._extract_location_from_text(text_content),
            'description': self._extract_description_from_content(soup),
            'requirements': self._extract_requirements_from_text(text_content),
            'responsibilities': self._extract_responsibilities_from_text(text_content),
            'salary_range': self._extract_salary_from_text(text_content),
        }
        
        return job_data
    
    def _scrape_with_text_mining(self, soup: BeautifulSoup, url: str) -> Dict:
        """Last resort: extract any meaningful content using text mining"""
        
        # Get main content area
        main_content = self._find_main_content_area(soup)
        
        # Extract title from page title and headings
        title = self._extract_title_from_elements(soup)
        
        # Extract company from various patterns
        company = self._extract_company_from_patterns(soup)
        
        # Get description from main content
        description = main_content.get_text() if main_content else soup.get_text()
        
        # Clean up description
        description = self._clean_text(description)
        
        return {
            'title': title,
            'company': company,
            'description': description[:5000],  # Limit description length
            'raw_content': description,
            'extraction_method': 'text_mining'
        }
    
    def _scrape_linkedin_enhanced(self, soup: BeautifulSoup) -> Dict:
        """Enhanced LinkedIn scraping with updated selectors"""
        
        selectors = {
            'title': [
                'h1.t-24.t-bold.inline',
                'h1[class*="job-title"]',
                'h1[class*="jobPosting"]',
                '.job-details-jobs-unified-top-card__job-title',
                '.jobs-unified-top-card__job-title',
                'h1.jobs-unified-top-card__job-title-link',
                'h1'
            ],
            'company': [
                '.job-details-jobs-unified-top-card__company-name',
                '.jobs-unified-top-card__company-name',
                'a[data-control-name="job_details_topcard_company_url"]',
                '.jobs-unified-top-card__company-name a',
                '.company-name'
            ],
            'location': [
                '.job-details-jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__location',
                '[class*="location"]'
            ],
            'description': [
                '.jobs-description-content__text',
                '.jobs-box__html-content',
                '.jobs-description',
                '[class*="description"]'
            ]
        }
        
        return self._extract_using_selectors(soup, selectors)
    
    def _scrape_indeed_enhanced(self, soup: BeautifulSoup) -> Dict:
        """Enhanced Indeed scraping with updated selectors"""
        
        selectors = {
            'title': [
                'h1[data-testid="jobsearch-JobInfoHeader-title"]',
                'h1.jobsearch-JobInfoHeader-title',
                '.jobsearch-JobInfoHeader-title',
                'h1[class*="jobTitle"]',
                'h1'
            ],
            'company': [
                '[data-testid="inlineHeader-companyName"]',
                '.jobsearch-InlineCompanyRating',
                '.jobsearch-JobInfoHeader-subtitle a',
                '[class*="companyName"]'
            ],
            'location': [
                '[data-testid="job-location"]',
                '.jobsearch-JobMetadataHeader-iconLabel',
                '[class*="location"]'
            ],
            'description': [
                '#jobDescriptionText',
                '.jobsearch-jobDescriptionText',
                '[class*="jobDescription"]',
                '.job-description'
            ]
        }
        
        return self._extract_using_selectors(soup, selectors)
    
    def _scrape_glassdoor_enhanced(self, soup: BeautifulSoup) -> Dict:
        """Enhanced Glassdoor scraping with updated selectors"""
        
        selectors = {
            'title': [
                '[data-test="job-title"]',
                '.jobTitle',
                '[class*="jobTitle"]',
                'h1'
            ],
            'company': [
                '[data-test="employer-name"]',
                '.employerName',
                '[class*="employer"]',
                '[class*="company"]'
            ],
            'location': [
                '[data-test="job-location"]',
                '.location',
                '[class*="location"]'
            ],
            'description': [
                '[data-test="jobDescriptionContent"]',
                '.jobDescriptionContent',
                '[class*="description"]'
            ]
        }
        
        return self._extract_using_selectors(soup, selectors)
    
    def _scrape_generic_enhanced(self, soup: BeautifulSoup) -> Dict:
        """Enhanced generic scraping for any job site"""
        
        selectors = {
            'title': [
                'h1[class*="job"]',
                'h1[class*="title"]',
                'h1[class*="position"]',
                'h1[id*="job"]',
                'h1[id*="title"]',
                '.job-title',
                '.position-title',
                '.role-title',
                'h1',
                'h2[class*="job"]',
                'h2[class*="title"]'
            ],
            'company': [
                '[class*="company"]',
                '[class*="employer"]',
                '[class*="organization"]',
                '[id*="company"]',
                'a[href*="company"]',
                '.company-name',
                '.employer-name'
            ],
            'location': [
                '[class*="location"]',
                '[class*="address"]',
                '[class*="city"]',
                '[id*="location"]',
                '.location',
                '.address'
            ],
            'description': [
                '[class*="description"]',
                '[class*="content"]',
                '[class*="details"]',
                '[id*="description"]',
                '.job-description',
                '.job-content',
                '.job-details'
            ]
        }
        
        return self._extract_using_selectors(soup, selectors)
    
    def _extract_using_selectors(self, soup: BeautifulSoup, selectors: Dict[str, List[str]]) -> Dict:
        """Extract job data using provided selectors"""
        
        job_data = {}
        
        for field, selector_list in selectors.items():
            text = self._extract_text_by_selectors(soup, selector_list)
            if text:
                job_data[field] = text
        
        # Enhance with additional extraction
        if job_data:
            job_data = self._enhance_job_data(job_data, soup)
        
        return job_data
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try multiple selectors and return first successful extraction"""
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) > 2:  # Must be meaningful text
                        return self._clean_text(text)
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return None
    
    def _extract_title_from_elements(self, soup: BeautifulSoup) -> str:
        """Extract job title from various page elements"""
        
        # Try page title first
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Clean up page title (remove site name, etc.)
            title_parts = title_text.split(' - ')[0].split(' | ')[0].split(' at ')[0]
            if len(title_parts) > 5:
                return self._clean_text(title_parts)
        
        # Try h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            text = h1.get_text().strip()
            if text and 10 <= len(text) <= 200:  # Reasonable title length
                return self._clean_text(text)
        
        # Try other heading tags
        for tag in ['h2', 'h3']:
            headings = soup.find_all(tag)
            for heading in headings:
                text = heading.get_text().strip()
                if text and any(keyword in text.lower() for keyword in ['job', 'position', 'role', 'career']):
                    return self._clean_text(text)
        
        return "Position Title Not Available"
    
    def _extract_company_from_patterns(self, soup: BeautifulSoup) -> str:
        """Extract company name using various patterns"""
        
        # Look for company in URL
        url_patterns = soup.find('link', {'rel': 'canonical'})
        if url_patterns:
            href = url_patterns.get('href', '')
            company_from_url = self._extract_company_from_url(href)
            if company_from_url:
                return company_from_url
        
        # Look for links with company indicators
        company_links = soup.find_all('a', href=True)
        for link in company_links:
            href = link.get('href', '').lower()
            if any(indicator in href for indicator in ['company', 'employer', 'organization']):
                text = link.get_text().strip()
                if text and 2 <= len(text) <= 100:
                    return self._clean_text(text)
        
        # Look for text patterns that indicate company names
        all_text = soup.get_text()
        company_patterns = [
            r'(?i)(?:at|by|for)\s+([A-Z][A-Za-z\s&.,]+?)(?:\s+(?:is|seeks|looking))',
            r'(?i)([A-Z][A-Za-z\s&.,]+?)\s+(?:is hiring|seeks|looking for)',
            r'(?i)company:\s*([A-Z][A-Za-z\s&.,]+)',
            r'(?i)employer:\s*([A-Z][A-Za-z\s&.,]+)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                company = matches[0].strip()
                if 2 <= len(company) <= 100:
                    return self._clean_text(company)
        
        return "Company Not Available"
    
    def _extract_company_from_url(self, url: str) -> Optional[str]:
        """Extract company name from URL patterns"""
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Common company domain patterns
        if 'careers.' in domain or 'jobs.' in domain:
            # Extract main domain
            main_domain = domain.replace('careers.', '').replace('jobs.', '').replace('www.', '')
            company_name = main_domain.split('.')[0]
            if len(company_name) > 2:
                return company_name.replace('-', ' ').title()
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common job board artifacts
        artifacts = [
            'Apply Now', 'View Job', 'Save Job', 'Share Job',
            'Quick Apply', 'Easy Apply', 'Apply on Company Website',
            '(opens in a new window)', '(opens in new tab)'
        ]
        
        for artifact in artifacts:
            text = text.replace(artifact, '')
        
        return text.strip()
    
    def _is_valid_extraction(self, job_data: Dict) -> bool:
        """Validate that we extracted meaningful job data"""
        
        if not job_data:
            return False
        
        # Must have at least title or company
        has_title = job_data.get('title') and len(job_data['title'].strip()) > 3
        has_company = job_data.get('company') and len(job_data['company'].strip()) > 2
        has_description = job_data.get('description') and len(job_data['description'].strip()) > 50
        
        # Check for "Not Available" placeholders
        title_valid = has_title and 'not available' not in job_data.get('title', '').lower()
        company_valid = has_company and 'not available' not in job_data.get('company', '').lower()
        
        return (title_valid or company_valid) and (has_description or has_title or has_company)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False
    
    def _detect_job_site(self, url: str) -> str:
        """Detect which job site we're scraping"""
        url_lower = url.lower()
        
        if 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'indeed.com' in url_lower:
            return 'indeed'
        elif 'glassdoor.com' in url_lower:
            return 'glassdoor'
        elif 'monster.com' in url_lower:
            return 'monster'
        elif 'ziprecruiter.com' in url_lower:
            return 'ziprecruiter'
        else:
            return 'generic'
    
    def _enhance_job_data(self, job_data: Dict, soup: BeautifulSoup) -> Dict:
        """Enhance job data with additional extracted information"""
        
        # Extract additional fields if not already present
        if not job_data.get('requirements'):
            job_data['requirements'] = self._extract_requirements_from_soup(soup)
        
        if not job_data.get('responsibilities'):
            job_data['responsibilities'] = self._extract_responsibilities_from_soup(soup)
        
        if not job_data.get('salary_range'):
            job_data['salary_range'] = self._extract_salary_from_soup(soup)
        
        if not job_data.get('employment_type'):
            job_data['employment_type'] = self._extract_employment_type_from_soup(soup)
        
        # Add metadata
        job_data['raw_content'] = soup.get_text()[:10000]  # First 10k chars
        job_data['extraction_timestamp'] = time.time()
        
        return job_data
    
    def _create_fallback_result(self, url: str, error_message: str) -> Dict:
        """Create a fallback result when scraping fails"""
        return {
            'title': 'Extraction Failed - Manual Review Required',
            'company': 'Unknown Company',
            'description': f'Automatic extraction failed: {error_message}. Please review manually.',
            'location': 'Location Not Available',
            'requirements': 'Requirements extraction failed',
            'responsibilities': 'Responsibilities extraction failed',
            'salary_range': '',
            'employment_type': '',
            'raw_content': f'URL: {url}\\nError: {error_message}',
            'extraction_error': error_message,
            'needs_manual_review': True
        }
    
    def _create_intelligent_fallback(self, soup: BeautifulSoup, url: str) -> Dict:
        """Create an intelligent fallback with whatever we can extract"""
        
        # Get the best available title
        title = self._extract_title_from_elements(soup)
        
        # Get the best available company
        company = self._extract_company_from_patterns(soup)
        
        # Get main content
        main_content = self._find_main_content_area(soup)
        description = main_content.get_text() if main_content else soup.get_text()
        description = self._clean_text(description)[:5000]
        
        return {
            'title': title,
            'company': company,
            'description': description,
            'location': self._extract_location_from_text(description),
            'requirements': self._extract_requirements_from_text(description),
            'responsibilities': self._extract_responsibilities_from_text(description),
            'salary_range': self._extract_salary_from_text(description),
            'employment_type': '',
            'raw_content': description,
            'extraction_method': 'intelligent_fallback',
            'needs_review': True
        }
    
    def _find_main_content_area(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the main content area of the page"""
        
        # Try semantic HTML5 tags first
        for tag in ['main', 'article', '[role="main"]']:
            element = soup.select_one(tag)
            if element:
                return element
        
        # Try common content container IDs/classes
        content_selectors = [
            '#content', '#main-content', '#job-content',
            '.content', '.main-content', '.job-content',
            '.container', '.wrapper', '.job-details'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text().strip()) > 200:
                return element
        
        # Fallback to body
        return soup.find('body')
    
    def _extract_requirements_from_text(self, text: str) -> str:
        """Extract requirements from text using pattern matching"""
        
        requirement_patterns = [
            r'(?i)(?:requirements?|qualifications?|skills?|experience)[:\-]?\s*(.{50,500}?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)(?:you.{1,20}?(?:have|need|must))[:\-]?\s*(.{50,500}?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)(?:candidates?.{1,20}?(?:should|must|need))[:\-]?\s*(.{50,500}?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return self._clean_text(matches[0])
        
        return ''
    
    def _extract_responsibilities_from_text(self, text: str) -> str:
        """Extract responsibilities from text using pattern matching"""
        
        responsibility_patterns = [
            r'(?i)(?:responsibilities|duties|tasks|role)[:\-]?\s*(.{50,500}?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)(?:you will|you.{1,20}?(?:be responsible|handle|manage))[:\-]?\s*(.{50,500}?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return self._clean_text(matches[0])
        
        return ''
    
    def _extract_salary_from_text(self, text: str) -> str:
        """Extract salary information from text"""
        
        salary_patterns = [
            r'\\$[\\d,]+(?:\\.\\d{2})?(?:\\s*-\\s*\\$[\\d,]+(?:\\.\\d{2})?)?(?:\\s*(?:per|/)?\\s*(?:year|yr|hour|hr|month))?',
            r'(?i)(?:salary|compensation|pay)[:\\s]*\\$[\\d,]+(?:\\.\\d{2})?(?:\\s*-\\s*\\$[\\d,]+(?:\\.\\d{2})?)?',
            r'(?i)[\\d,]+k?(?:\\s*-\\s*[\\d,]+k?)?\\s*(?:per|/)?\\s*(?:year|annual|yearly)'
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return ''
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from text"""
        
        location_patterns = [
            r'(?i)(?:location|address|based in)[:\\s]*([A-Za-z\\s,]+)(?:\\n|$)',
            r'([A-Z][a-z]+,\\s*[A-Z]{2}(?:\\s+\\d{5})?)',  # City, State ZIP
            r'([A-Z][a-z]+\\s[A-Z][a-z]+,\\s*[A-Z]{2})',   # City Name, State
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return self._clean_text(matches[0])
        
        return ''
    
    def _extract_company_from_structured_data(self, data: Dict) -> str:
        """Extract company from structured data"""
        
        hiring_org = data.get('hiringOrganization', {})
        if isinstance(hiring_org, dict):
            return hiring_org.get('name', '')
        elif isinstance(hiring_org, str):
            return hiring_org
        
        return data.get('organizationName', '')
    
    def _extract_location_from_structured_data(self, data: Dict) -> str:
        """Extract location from structured data"""
        
        job_location = data.get('jobLocation', {})
        if isinstance(job_location, dict):
            address = job_location.get('address', {})
            if isinstance(address, dict):
                city = address.get('addressLocality', '')
                state = address.get('addressRegion', '')
                return f"{city}, {state}".strip(', ')
        
        return ''
    
    def _extract_salary_from_structured_data(self, data: Dict) -> str:
        """Extract salary from structured data"""
        
        base_salary = data.get('baseSalary', {})
        if isinstance(base_salary, dict):
            value = base_salary.get('value', {})
            if isinstance(value, dict):
                min_val = value.get('minValue', '')
                max_val = value.get('maxValue', '')
                currency = value.get('currency', '$')
                
                if min_val and max_val:
                    return f"{currency}{min_val} - {currency}{max_val}"
                elif min_val:
                    return f"{currency}{min_val}+"
        
        return ''
    
    def _extract_microdata(self, soup: BeautifulSoup) -> Dict:
        """Extract microdata from HTML"""
        # This is a simplified microdata extraction
        # In a full implementation, you'd parse microdata more thoroughly
        return {}
    
    def _extract_requirements_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract requirements from soup using selectors"""
        
        requirement_selectors = [
            '[class*="requirement"]', '[id*="requirement"]',
            '[class*="qualification"]', '[id*="qualification"]',
            '[class*="skill"]', '[id*="skill"]'
        ]
        
        for selector in requirement_selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        return ''
    
    def _extract_responsibilities_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract responsibilities from soup using selectors"""
        
        responsibility_selectors = [
            '[class*="responsibility"]', '[id*="responsibility"]',
            '[class*="duties"]', '[id*="duties"]',
            '[class*="role"]', '[id*="role"]'
        ]
        
        for selector in responsibility_selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        return ''
    
    def _extract_salary_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract salary from soup using selectors"""
        
        salary_selectors = [
            '[class*="salary"]', '[id*="salary"]',
            '[class*="compensation"]', '[id*="compensation"]',
            '[class*="pay"]', '[id*="pay"]'
        ]
        
        for selector in salary_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text()
                if '$' in text or any(term in text.lower() for term in ['salary', 'pay', 'compensation']):
                    return self._clean_text(text)
        
        return ''
    
    def _extract_employment_type_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract employment type from soup"""
        
        employment_types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance']
        text = soup.get_text().lower()
        
        for emp_type in employment_types:
            if emp_type in text:
                return emp_type.title()
        
        return ''
