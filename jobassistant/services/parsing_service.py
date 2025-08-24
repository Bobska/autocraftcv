"""
Resume parsing service with both free and paid options
"""

import pdfplumber
import fitz  # PyMuPDF
from docx import Document
import requests
import json
import re
from typing import Dict, Optional, List
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
import logging

logger = logging.getLogger(__name__)


class ResumeParsingService:
    """Service for parsing resume files and extracting structured information"""
    
    def __init__(self, use_paid_apis: bool = False):
        self.use_paid_apis = use_paid_apis
    
    def parse_resume(self, file: UploadedFile) -> Dict:
        """
        Main method to parse resume file
        Returns dictionary with structured resume data
        """
        try:
            if self.use_paid_apis:
                return self._parse_with_paid_apis(file)
            else:
                return self._parse_with_free_tools(file)
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return {'error': str(e)}
    
    def _parse_with_paid_apis(self, file: UploadedFile) -> Dict:
        """Parse using paid APIs like Affinda or RChilli"""
        
        # Try Affinda first
        affinda_key = getattr(settings, 'AFFINDA_API_KEY', None)
        if affinda_key:
            try:
                result = self._parse_with_affinda(file, affinda_key)
                if result and not result.get('error'):
                    return result
            except Exception as e:
                logger.warning(f"Affinda parsing failed: {e}")
        
        # Fallback to free tools
        return self._parse_with_free_tools(file)
    
    def _parse_with_affinda(self, file: UploadedFile, api_key: str) -> Dict:
        """Parse using Affinda Resume Parser API"""
        url = "https://api.affinda.com/v3/documents"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
        }
        
        files = {
            'file': (file.name, file.read(), file.content_type)
        }
        
        data = {
            'collection': 'resumes'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        return self._convert_affinda_response(result)
    
    def _convert_affinda_response(self, affinda_data: Dict) -> Dict:
        """Convert Affinda API response to our standard format"""
        data = affinda_data.get('data', {})
        
        return {
            'full_name': self._safe_get(data, 'name', 'raw'),
            'email': self._safe_get(data, 'emails', 0, 'email'),
            'phone': self._safe_get(data, 'phoneNumbers', 0, 'rawNumber'),
            'location': self._format_location(data.get('location')),
            'professional_summary': data.get('summary', ''),
            'technical_skills': self._extract_skills(data.get('skills', [])),
            'education': self._format_education(data.get('education', [])),
            'work_experience': self._format_work_experience(data.get('workExperience', [])),
            'certifications': self._format_certifications(data.get('certifications', [])),
            'linkedin_url': self._extract_linkedin(data.get('websites', [])),
            'raw_text': data.get('rawText', ''),
        }
    
    def _parse_with_free_tools(self, file: UploadedFile) -> Dict:
        """Parse using free tools (pdfplumber, PyMuPDF, python-docx)"""
        
        file_extension = file.name.lower().split('.')[-1]
        
        try:
            if file_extension == 'pdf':
                text = self._extract_text_from_pdf(file)
            elif file_extension in ['doc', 'docx']:
                text = self._extract_text_from_docx(file)
            else:
                return {'error': 'Unsupported file format'}
            
            if not text.strip():
                return {'error': 'Could not extract text from file'}
            
            return self._parse_text_content(text)
            
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            return {'error': f'Failed to parse file: {str(e)}'}
    
    def _extract_text_from_pdf(self, file: UploadedFile) -> str:
        """Extract text from PDF using pdfplumber and PyMuPDF as fallback"""
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        
        # Try PyMuPDF as fallback
        try:
            file.seek(0)  # Reset file pointer
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            
            pdf_document.close()
            return text
            
        except Exception as e:
            logger.error(f"PyMuPDF also failed: {e}")
            raise e
    
    def _extract_text_from_docx(self, file: UploadedFile) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file)
            text = []
            
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            return "\n".join(text)
            
        except Exception as e:
            logger.error(f"Error reading Word document: {e}")
            raise e
    
    def _parse_text_content(self, text: str) -> Dict:
        """Parse structured information from raw text"""
        
        parsed_data = {
            'full_name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'location': self._extract_location(text),
            'professional_summary': self._extract_summary(text),
            'technical_skills': self._extract_skills_from_text(text),
            'soft_skills': self._extract_soft_skills_from_text(text),
            'education': self._extract_education_from_text(text),
            'work_experience': self._extract_work_experience_from_text(text),
            'certifications': self._extract_certifications_from_text(text),
            'achievements': self._extract_achievements_from_text(text),
            'linkedin_url': self._extract_linkedin_from_text(text),
            'portfolio_url': self._extract_portfolio_from_text(text),
            'raw_text': text,
        }
        
        return parsed_data
    
    def _extract_name(self, text: str) -> str:
        """Extract full name from text"""
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            # Look for lines that likely contain names
            if len(line.split()) >= 2 and len(line.split()) <= 4:
                # Check if it's not an email, phone, or address
                if not re.search(r'[@\(\)\-\d]', line) and not line.lower().startswith(('email', 'phone', 'address')):
                    # Check if words are capitalized (name pattern)
                    words = line.split()
                    if all(word[0].isupper() for word in words if word):
                        return line
        
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
            r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
            r'\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Various formats
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location/address from text"""
        # Look for common location patterns
        location_patterns = [
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, ST
            r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',  # City, State
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2}\b'  # City Name, ST
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        summary_patterns = [
            r'(?:summary|objective|profile)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|\nskills|$)',
            r'(?:professional summary|career objective)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|\nskills|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50:  # Ensure it's substantial
                    return summary
        
        # If no explicit summary found, try to extract the first paragraph after name/contact
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if len(line.strip()) > 100 and not re.search(r'[@\(\)\-\d]', line):
                return line.strip()
        
        return ""
    
    def _extract_skills_from_text(self, text: str) -> str:
        """Extract technical skills from text"""
        skills_patterns = [
            r'(?:technical skills?|technologies?|programming languages?)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|$)',
            r'(?:skills?)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|$)'
        ]
        
        for pattern in skills_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1).strip()
                # Clean up the skills text
                skills = re.split(r'[,\n•\-\*]', skills_text)
                skills = [skill.strip() for skill in skills if skill.strip()]
                return ', '.join(skills[:20])  # Limit to first 20 skills
        
        # Look for common technical skills
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Swift',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'SQL', 'MongoDB',
            'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Jenkins', 'CI/CD'
        ]
        
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        return ', '.join(found_skills) if found_skills else ""
    
    def _extract_soft_skills_from_text(self, text: str) -> str:
        """Extract soft skills from text"""
        common_soft_skills = [
            'Leadership', 'Communication', 'Teamwork', 'Problem Solving',
            'Critical Thinking', 'Time Management', 'Project Management',
            'Analytical', 'Creative', 'Adaptable', 'Detail-oriented'
        ]
        
        found_skills = []
        for skill in common_soft_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        return ', '.join(found_skills) if found_skills else ""
    
    def _extract_education_from_text(self, text: str) -> str:
        """Extract education information"""
        education_patterns = [
            r'(?:education|academic)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\nskills|$)',
            r'(?:degree|university|college)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\nskills|$)'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Look for degree patterns
        degree_patterns = [
            r'(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?(?:in|of)\s+[A-Za-z\s]+',
            r'(?:Bachelor|Master|PhD).*?(?:\d{4}|\d{2})'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return '\n'.join(matches)
        
        return ""
    
    def _extract_work_experience_from_text(self, text: str) -> str:
        """Extract work experience"""
        experience_patterns = [
            r'(?:experience|employment|work history)[:\n\s]*([^§]*?)(?=\n\n|\neducation|\nskills|$)',
            r'(?:professional experience)[:\n\s]*([^§]*?)(?=\n\n|\neducation|\nskills|$)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_certifications_from_text(self, text: str) -> str:
        """Extract certifications"""
        cert_patterns = [
            r'(?:certifications?|licenses?)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|\nskills|$)'
        ]
        
        for pattern in cert_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_achievements_from_text(self, text: str) -> str:
        """Extract achievements and accomplishments"""
        achievement_patterns = [
            r'(?:achievements?|accomplishments?|awards?)[:\n\s]*([^§]*?)(?=\n\n|\n[A-Z]|\nexperience|\neducation|\nskills|$)'
        ]
        
        for pattern in achievement_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_linkedin_from_text(self, text: str) -> str:
        """Extract LinkedIn URL"""
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9\-]+'
        matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        return matches[0] if matches else ""
    
    def _extract_portfolio_from_text(self, text: str) -> str:
        """Extract portfolio URL"""
        # Look for personal websites (excluding social media)
        url_pattern = r'https?://[A-Za-z0-9\-\.]+\.[A-Za-z]{2,}'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            # Filter out common social media and email domains
            excluded_domains = ['linkedin.com', 'twitter.com', 'facebook.com', 'gmail.com', 'yahoo.com']
            if not any(domain in url.lower() for domain in excluded_domains):
                return url
        
        return ""
    
    # Helper methods for paid API parsing
    def _safe_get(self, data: Dict, *keys) -> str:
        """Safely get nested dictionary values"""
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and isinstance(key, int) and len(current) > key:
                current = current[key]
            else:
                return ""
        return str(current) if current else ""
    
    def _format_location(self, location_data: Dict) -> str:
        """Format location data from API"""
        if not location_data:
            return ""
        
        parts = []
        if location_data.get('city'):
            parts.append(location_data['city'])
        if location_data.get('state'):
            parts.append(location_data['state'])
        if location_data.get('country'):
            parts.append(location_data['country'])
        
        return ', '.join(parts)
    
    def _extract_skills(self, skills_data: List) -> str:
        """Extract skills from API response"""
        if not skills_data:
            return ""
        
        skills = []
        for skill in skills_data:
            if isinstance(skill, dict) and skill.get('name'):
                skills.append(skill['name'])
            elif isinstance(skill, str):
                skills.append(skill)
        
        return ', '.join(skills[:20])  # Limit to 20 skills
    
    def _format_education(self, education_data: List) -> str:
        """Format education data from API"""
        if not education_data:
            return ""
        
        formatted = []
        for edu in education_data:
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('dates', {}).get('completionDate', '') if edu.get('dates') else ''
                
                if degree and institution:
                    edu_str = f"{degree} - {institution}"
                    if year:
                        edu_str += f" ({year})"
                    formatted.append(edu_str)
        
        return '\n'.join(formatted)
    
    def _format_work_experience(self, work_data: List) -> str:
        """Format work experience data from API"""
        if not work_data:
            return ""
        
        formatted = []
        for job in work_data:
            if isinstance(job, dict):
                title = job.get('jobTitle', '')
                company = job.get('organization', '')
                dates = job.get('dates', {})
                start_date = dates.get('startDate', '') if dates else ''
                end_date = dates.get('endDate', '') if dates else ''
                
                if title and company:
                    job_str = f"{title} | {company}"
                    if start_date or end_date:
                        job_str += f" | {start_date} - {end_date or 'Present'}"
                    
                    if job.get('jobDescription'):
                        job_str += f"\n{job['jobDescription']}"
                    
                    formatted.append(job_str)
        
        return '\n\n'.join(formatted)
    
    def _format_certifications(self, cert_data: List) -> str:
        """Format certifications data from API"""
        if not cert_data:
            return ""
        
        certs = []
        for cert in cert_data:
            if isinstance(cert, dict) and cert.get('name'):
                certs.append(cert['name'])
            elif isinstance(cert, str):
                certs.append(cert)
        
        return '\n'.join(certs)
    
    def _extract_linkedin(self, websites_data: List) -> str:
        """Extract LinkedIn URL from websites data"""
        if not websites_data:
            return ""
        
        for website in websites_data:
            if isinstance(website, dict) and website.get('url'):
                url = website['url']
                if 'linkedin.com' in url:
                    return url
        
        return ""
