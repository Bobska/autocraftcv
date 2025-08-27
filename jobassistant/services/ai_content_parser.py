"""
AI-Powered Job Content Parser for Manual Entry Fallback
"""

import re
import json
import logging
from typing import Dict, Optional, List
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class AIJobContentParser:
    """AI-powered parser for manually entered job content"""
    
    def __init__(self):
        self.patterns = self.init_extraction_patterns()
    
    def init_extraction_patterns(self) -> Dict:
        """Initialize regex patterns for content extraction"""
        
        return {
            'title': [
                r'(?i)(?:job\s+title|position|role)[:\s-]+(.+?)(?:\n|$)',
                r'(?i)^(.+?)(?:\s*-\s*(?:job|position|role|career))',
                r'(?i)(.+?)(?:\s+at\s+\w+)',
                r'(?i)^([A-Z][A-Za-z\s&,.-]+?)(?:\n)',
            ],
            'company': [
                r'(?i)(?:company|employer|organization)[:\s-]+(.+?)(?:\n|$)',
                r'(?i)(?:at|with|for)\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s+(?:in|located|based))',
                r'(?i)([A-Z][A-Za-z\s&,.-]+?)\s+(?:is\s+)?(?:seeking|looking|hiring)',
                r'(?i)join\s+(?:the\s+team\s+at\s+)?([A-Z][A-Za-z\s&,.-]+)',
            ],
            'location': [
                r'(?i)(?:location|address|based\s+in)[:\s-]+(.+?)(?:\n|$)',
                r'([A-Z][a-z]+,\s*[A-Z]{2,3}(?:\s+\d{4,5})?)',  # City, State/Country
                r'([A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2,3})',   # City Name, State
                r'(?i)(?:remote|work\s+from\s+home|wfh)',
            ],
            'salary': [
                r'\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?(?:\s*(?:per|/)\s*(?:year|yr|hour|hr|annum))?',
                r'(?i)(?:salary|compensation|pay)[:\s]*\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?',
                r'(?i)[\d,]+k?(?:\s*-\s*[\d,]+k?)?\s*(?:per|/)\s*(?:year|annual|yearly)',
                r'(?i)AUD?\s*[\d,]+(?:\s*-\s*[\d,]+)?',
            ],
            'requirements': [
                r'(?i)(?:requirements?|qualifications?|skills?|experience)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:you\s+(?:will\s+)?(?:have|need|must|require))[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:essential|required|must\s+have)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:minimum\s+requirements?)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
            ],
            'responsibilities': [
                r'(?i)(?:responsibilities|duties|tasks|role)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:you\s+will|you\'ll|you\s+would)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:job\s+description|about\s+(?:the\s+)?(?:role|position))[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
                r'(?i)(?:key\s+responsibilities)[:\s-]+((?:.|\n)+?)(?:\n\n|\n[A-Z][^a-z]|$)',
            ],
            'employment_type': [
                r'(?i)(full-?time|part-?time|contract|temporary|permanent|casual|internship|graduate)',
                r'(?i)(full\s+time|part\s+time)',
            ]
        }
    
    def parse_job_content(self, raw_content: str, job_url: Optional[str] = None) -> Dict:
        """Main method to parse job content using AI and regex"""
        
        logger.info(f"Starting AI parsing for job content (length: {len(raw_content)})")
        
        # Clean the content first
        cleaned_content = self.clean_content(raw_content)
        
        # Try AI parsing first
        ai_result = self.parse_with_ai(cleaned_content)
        
        # Fallback to regex parsing for any missing fields
        regex_result = self.parse_with_regex(cleaned_content)
        
        # Combine results (AI takes priority)
        final_result = self.combine_parsing_results(ai_result, regex_result, job_url or '')
        
        # Validate and enhance
        final_result = self.validate_and_enhance(final_result, cleaned_content)
        
        logger.info(f"Parsing complete. AI success: {bool(ai_result)}, Final quality: {self.assess_quality(final_result)}")
        
        return final_result
    
    def clean_content(self, raw_content: str) -> str:
        """Clean raw content for better parsing"""
        
        # First, remove JSON-encoded content contamination
        cleaned = self.remove_json_encoded_content(raw_content)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        # Remove common web elements
        web_artifacts = [
            r'cookie\s+policy.*?(?:\n|$)',
            r'privacy\s+policy.*?(?:\n|$)',
            r'terms\s+(?:and\s+conditions|of\s+service).*?(?:\n|$)',
            r'subscribe\s+to\s+(?:our\s+)?newsletter.*?(?:\n|$)',
            r'follow\s+us\s+on\s+social\s+media.*?(?:\n|$)',
            r'share\s+this\s+job.*?(?:\n|$)',
            r'apply\s+now.*?(?:\n|$)',
            r'save\s+(?:this\s+)?job.*?(?:\n|$)',
            r'back\s+to\s+(?:search\s+)?results.*?(?:\n|$)',
            r'view\s+all\s+jobs.*?(?:\n|$)',
        ]
        
        for pattern in web_artifacts:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove URLs
        cleaned = re.sub(r'https?://[^\s]+', '', cleaned)
        
        # Remove email addresses
        cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', cleaned)
        
        # Clean up remaining whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
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
            
            # If more than 10% of the content is JSON-encoded, or more than 50 matches, discard it
            contamination_percentage = (encoded_matches / total_length * 100) if total_length > 0 else 0
            if contamination_percentage > 10 or encoded_matches > 50:
                logger.warning(f"Discarding content with high JSON encoding contamination ({contamination_percentage:.1f}%, {encoded_matches} matches)")
                return ""
        
        # Remove specific JSON-encoded artifacts
        text = re.sub(r'\\u003C.*?\\u003E', '', text)  # Remove <tag> patterns
        text = re.sub(r'\\u002F', '/', text)  # Convert \u002F to /
        text = re.sub(r'\\[\'"]', '', text)  # Remove escaped quotes
        
        return text.strip()
    
    def parse_with_ai(self, content: str) -> Optional[Dict]:
        """Parse content using AI (free local model or API)"""
        
        try:
            # Try free AI parsing options
            
            # Option 1: Use local AI model (Ollama, etc.)
            if hasattr(settings, 'USE_LOCAL_AI') and settings.USE_LOCAL_AI:
                return self.parse_with_local_ai(content)
            
            # Option 2: Use free online AI service
            if hasattr(settings, 'FREE_AI_API_KEY') and settings.FREE_AI_API_KEY:
                return self.parse_with_free_ai_api(content)
            
            # Option 3: Use simple rule-based "AI" (pattern matching)
            return self.parse_with_smart_patterns(content)
            
        except Exception as e:
            logger.warning(f"AI parsing failed: {str(e)}")
            return None
    
    def parse_with_local_ai(self, content: str) -> Optional[Dict]:
        """Parse using local AI model (Ollama, etc.)"""
        
        try:
            # This would connect to a local Ollama instance
            prompt = self.create_ai_prompt(content)
            
            # Example Ollama API call
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': 'llama3.2',  # or another free model
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                return self.parse_ai_response(generated_text)
            
        except Exception as e:
            logger.debug(f"Local AI parsing failed: {str(e)}")
        
        return None
    
    def parse_with_free_ai_api(self, content: str) -> Optional[Dict]:
        """Parse using free AI API (Hugging Face, etc.)"""
        
        try:
            # Example using Hugging Face Inference API (free tier)
            api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
            
            if not api_key:
                return None
            
            prompt = self.create_ai_prompt(content)
            
            response = requests.post(
                'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
                headers={'Authorization': f'Bearer {api_key}'},
                json={'inputs': prompt[:1000]},  # Limit for free tier
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    generated_text = result[0].get('generated_text', '')
                    return self.parse_ai_response(generated_text)
            
        except Exception as e:
            logger.debug(f"Free AI API parsing failed: {str(e)}")
        
        return None
    
    def parse_with_smart_patterns(self, content: str) -> Dict:
        """Advanced pattern-based parsing that simulates AI"""
        
        # This is a sophisticated rule-based system
        result = {}
        
        # Smart title extraction
        result['job_title'] = self.smart_extract_title(content)
        
        # Smart company extraction
        result['company_name'] = self.smart_extract_company(content)
        
        # Smart location extraction
        result['location'] = self.smart_extract_location(content)
        
        # Smart description extraction
        result['job_description'] = self.smart_extract_description(content)
        
        # Smart requirements extraction
        result['requirements'] = self.smart_extract_requirements(content)
        
        return result
    
    def smart_extract_title(self, content: str) -> str:
        """Smart title extraction using multiple strategies"""
        
        lines = content.split('\n')
        
        # Strategy 1: Look for lines that are likely titles
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Check if it's not a common header
                if not any(word in line.lower() for word in ['about', 'description', 'company', 'location']):
                    # Check if it contains job-related words
                    if any(word in line.lower() for word in ['manager', 'developer', 'analyst', 'coordinator', 'specialist', 'engineer', 'director', 'assistant']):
                        return line
        
        # Strategy 2: Use regex patterns
        for pattern in self.patterns['title']:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 100:
                    return title
        
        # Strategy 3: Look for the largest heading-like text
        potential_titles = []
        for line in lines[:15]:
            line = line.strip()
            if 15 <= len(line) <= 80 and not line.endswith('.'):
                potential_titles.append(line)
        
        if potential_titles:
            return potential_titles[0]
        
        return "Job Title Not Extracted"
    
    def smart_extract_company(self, content: str) -> str:
        """Smart company extraction"""
        
        # Strategy 1: Regex patterns
        for pattern in self.patterns['company']:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                company = match.group(1).strip()
                if 2 <= len(company) <= 50:
                    return company
        
        # Strategy 2: Look for patterns like "Join [Company]" or "About [Company]"
        about_patterns = [
            r'(?i)(?:about|join|at)\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s+(?:in|is|was|\n))',
            r'(?i)([A-Z][A-Za-z\s&,.-]+?)\s+is\s+(?:a|an|the)',
        ]
        
        for pattern in about_patterns:
            match = re.search(pattern, content)
            if match:
                company = match.group(1).strip()
                if 2 <= len(company) <= 50:
                    return company
        
        return "Company Not Extracted"
    
    def smart_extract_location(self, content: str) -> str:
        """Smart location extraction"""
        
        for pattern in self.patterns['location']:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                location = match.group(0 if pattern.startswith('(?i)(?:remote') else 1).strip()
                if len(location) > 2 and len(location) < 50:
                    return location
        
        return "Location Not Extracted"
    
    def smart_extract_description(self, content: str) -> str:
        """Smart job description extraction"""
        
        # Find the largest text block that looks like a description
        paragraphs = re.split(r'\n\n+', content)
        
        # Filter paragraphs that look like descriptions
        description_candidates = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 100:  # Must be substantial
                # Check if it contains job-related content
                job_indicators = ['responsible', 'manage', 'develop', 'work', 'experience', 'role', 'position']
                if any(indicator in para.lower() for indicator in job_indicators):
                    description_candidates.append(para)
        
        if description_candidates:
            # Return the longest relevant paragraph
            return max(description_candidates, key=len)
        
        # Fallback: return first substantial paragraph
        for para in paragraphs:
            para = para.strip()
            if len(para) > 100:
                return para
        
        return "Description Not Extracted"
    
    def smart_extract_requirements(self, content: str) -> str:
        """Smart requirements extraction"""
        
        for pattern in self.patterns['requirements']:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                requirements = match.group(1).strip()
                if len(requirements) > 20:
                    return requirements[:1000]  # Limit length
        
        return "Requirements Not Extracted"
    
    def create_ai_prompt(self, content: str) -> str:
        """Create AI prompt for job parsing"""
        
        return f"""
Extract job information from this job posting. Return ONLY valid JSON with these exact fields:

{{
    "job_title": "the job title/position",
    "company_name": "the hiring company name",
    "location": "job location (city, state/country)",
    "job_description": "main job responsibilities and duties",
    "requirements": "required qualifications, skills, experience"
}}

Job posting content:
{content[:2000]}

Return only the JSON object, no other text.
"""
    
    def parse_ai_response(self, ai_response: str) -> Optional[Dict]:
        """Parse AI response to extract structured data"""
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # If no JSON found, try to parse line by line
            result = {}
            lines = ai_response.split('\n')
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip().strip('"')
                    
                    if key in ['job_title', 'company_name', 'location', 'job_description', 'requirements']:
                        result[key] = value
            
            return result if result else None
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
            return None
    
    def parse_with_regex(self, content: str) -> Dict:
        """Fallback regex parsing for missing fields"""
        
        result = {}
        
        for field, patterns in self.patterns.items():
            if field == 'employment_type':
                # Special handling for employment type
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        result[field] = match.group(1 if '(' in pattern else 0)
                        break
            else:
                for pattern in patterns:
                    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
                    if match:
                        extracted = match.group(1).strip() if match.groups() else match.group(0).strip()
                        if len(extracted) > 2:
                            result[field] = extracted[:1000]  # Limit length
                            break
        
        return result
    
    def combine_parsing_results(self, ai_result: Optional[Dict], regex_result: Dict, job_url: str) -> Dict:
        """Combine AI and regex results, with AI taking priority"""
        
        # Start with regex results as base
        final_result = regex_result.copy()
        
        # Override with AI results if available and better
        if ai_result:
            for key, value in ai_result.items():
                if value and len(str(value).strip()) > 3:
                    # Map AI keys to our standard keys
                    standard_key = self.map_ai_key(key)
                    if standard_key:
                        final_result[standard_key] = str(value).strip()
        
        # Ensure all required fields exist
        required_fields = {
            'title': 'Manual Review Required',
            'company': 'Manual Review Required', 
            'location': 'Location Not Specified',
            'description': 'Description Not Available',
            'requirements': 'Requirements Not Specified',
            'employment_type': '',
            'salary_range': ''
        }
        
        for field, default in required_fields.items():
            if not final_result.get(field):
                final_result[field] = default
        
        # Add metadata
        final_result.update({
            'url': job_url or '',
            'extraction_method': 'ai_manual_parsing',
            'parsing_source': 'manual_entry',
            'ai_parsed': bool(ai_result),
            'needs_review': any('Manual Review Required' in str(v) for v in final_result.values())
        })
        
        return final_result
    
    def map_ai_key(self, ai_key: str) -> Optional[str]:
        """Map AI response keys to our standard field names"""
        
        key_mapping = {
            'job_title': 'title',
            'company_name': 'company',
            'job_description': 'description',
            'location': 'location',
            'requirements': 'requirements',
            'responsibilities': 'responsibilities',
            'salary': 'salary_range',
            'employment_type': 'employment_type'
        }
        
        return key_mapping.get(ai_key.lower().replace(' ', '_'))
    
    def validate_and_enhance(self, result: Dict, original_content: str) -> Dict:
        """Validate and enhance the parsing results"""
        
        # Clean up extracted text
        text_fields = ['title', 'company', 'location', 'description', 'requirements']
        
        for field in text_fields:
            if result.get(field):
                # Remove JSON-encoded content contamination
                result[field] = self.remove_json_encoded_content(result[field])
                
                # Remove excessive whitespace
                result[field] = ' '.join(result[field].split())
                
                # Remove common artifacts
                artifacts = ['Apply Now', 'Apply', 'Save Job', 'Share', 'Back to', 'View all']
                for artifact in artifacts:
                    result[field] = result[field].replace(artifact, '')
                
                result[field] = result[field].strip()
        
        # Extract salary if not already found
        if not result.get('salary_range'):
            salary_match = None
            for pattern in self.patterns['salary']:
                salary_match = re.search(pattern, original_content)
                if salary_match:
                    result['salary_range'] = salary_match.group(0)
                    break
        
        # Extract employment type if not found
        if not result.get('employment_type'):
            for pattern in self.patterns['employment_type']:
                emp_match = re.search(pattern, original_content, re.IGNORECASE)
                if emp_match:
                    result['employment_type'] = emp_match.group(1 if '(' in pattern else 0)
                    break
        
        # Add quality assessment
        result['extraction_quality'] = self.assess_quality(result)
        
        return result
    
    def assess_quality(self, result: Dict) -> str:
        """Assess the quality of extraction"""
        
        quality_score = 0
        
        # Title quality
        if result.get('title') and 'Manual Review Required' not in result['title']:
            quality_score += 2
        
        # Company quality  
        if result.get('company') and 'Manual Review Required' not in result['company']:
            quality_score += 2
        
        # Description quality
        if result.get('description') and len(result['description']) > 100:
            quality_score += 2
        
        # Requirements quality
        if result.get('requirements') and len(result['requirements']) > 50:
            quality_score += 1
        
        # Location quality
        if result.get('location') and 'Not Specified' not in result['location']:
            quality_score += 1
        
        if quality_score >= 6:
            return 'excellent'
        elif quality_score >= 4:
            return 'good'
        elif quality_score >= 2:
            return 'fair'
        else:
            return 'poor'
