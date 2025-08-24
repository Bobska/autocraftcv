"""
AI content generation service with both free and paid options
"""

import openai
import anthropic
import requests
import json
import re
from typing import Dict, Optional, List
from django.conf import settings
from django.template import Template, Context
import logging

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Service for generating cover letters and resumes using AI"""
    
    def __init__(self, use_paid_apis: bool = False):
        self.use_paid_apis = use_paid_apis
        self.setup_clients()
    
    def setup_clients(self):
        """Setup API clients for paid services"""
        if self.use_paid_apis:
            openai_key = getattr(settings, 'OPENAI_API_KEY', None)
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
            
            anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
    
    def generate_cover_letter(self, user_profile: Dict, job_posting: Dict, custom_instructions: str = "") -> Dict:
        """
        Generate a tailored cover letter
        Returns: {'content': str, 'method': str, 'generation_time': float}
        """
        import time
        start_time = time.time()
        
        try:
            if self.use_paid_apis:
                result = self._generate_cover_letter_paid(user_profile, job_posting, custom_instructions)
            else:
                result = self._generate_cover_letter_free(user_profile, job_posting, custom_instructions)
            
            result['generation_time'] = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            # Fallback to template-based generation
            result = self._generate_cover_letter_template(user_profile, job_posting, custom_instructions)
            result['generation_time'] = time.time() - start_time
            return result
    
    def generate_resume(self, user_profile: Dict, job_posting: Dict, custom_instructions: str = "") -> Dict:
        """
        Generate a tailored resume
        Returns: {'content': str, 'method': str, 'generation_time': float}
        """
        import time
        start_time = time.time()
        
        try:
            if self.use_paid_apis:
                result = self._generate_resume_paid(user_profile, job_posting, custom_instructions)
            else:
                result = self._generate_resume_free(user_profile, job_posting, custom_instructions)
            
            result['generation_time'] = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Error generating resume: {str(e)}")
            # Fallback to template-based generation
            result = self._generate_resume_template(user_profile, job_posting, custom_instructions)
            result['generation_time'] = time.time() - start_time
            return result
    
    def _generate_cover_letter_paid(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using paid APIs"""
        
        # Try OpenAI first
        if hasattr(self, 'openai_client'):
            try:
                return self._generate_cover_letter_openai(user_profile, job_posting, custom_instructions)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        
        # Try Anthropic
        if hasattr(self, 'anthropic_client'):
            try:
                return self._generate_cover_letter_anthropic(user_profile, job_posting, custom_instructions)
            except Exception as e:
                logger.warning(f"Anthropic failed: {e}")
        
        # Fallback to free methods
        return self._generate_cover_letter_free(user_profile, job_posting, custom_instructions)
    
    def _generate_cover_letter_openai(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using OpenAI GPT"""
        
        prompt = self._build_cover_letter_prompt(user_profile, job_posting, custom_instructions)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional career advisor and expert cover letter writer. Create compelling, personalized cover letters that highlight relevant experience and skills for specific job opportunities."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        return {
            'content': content,
            'method': 'openai'
        }
    
    def _generate_cover_letter_anthropic(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using Anthropic Claude"""
        
        prompt = self._build_cover_letter_prompt(user_profile, job_posting, custom_instructions)
        
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        return {
            'content': content,
            'method': 'anthropic'
        }
    
    def _generate_cover_letter_free(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using free methods"""
        
        # Try local Ollama first
        try:
            return self._generate_cover_letter_ollama(user_profile, job_posting, custom_instructions)
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
        
        # Try Hugging Face models
        try:
            return self._generate_cover_letter_huggingface(user_profile, job_posting, custom_instructions)
        except Exception as e:
            logger.warning(f"Hugging Face failed: {e}")
        
        # Fallback to template
        return self._generate_cover_letter_template(user_profile, job_posting, custom_instructions)
    
    def _generate_cover_letter_ollama(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using local Ollama model"""
        
        try:
            import ollama
            
            prompt = self._build_cover_letter_prompt(user_profile, job_posting, custom_instructions)
            
            response = ollama.chat(model='llama2', messages=[
                {
                    'role': 'system',
                    'content': 'You are a professional career advisor. Write compelling cover letters.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            return {
                'content': response['message']['content'],
                'method': 'ollama'
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise e
    
    def _generate_cover_letter_huggingface(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using Hugging Face transformers"""
        
        try:
            from transformers import pipeline, set_seed
            
            # Use a smaller model that can run locally
            generator = pipeline('text-generation', model='microsoft/DialoGPT-medium')
            set_seed(42)
            
            prompt = self._build_short_cover_letter_prompt(user_profile, job_posting, custom_instructions)
            
            result = generator(prompt, max_length=500, num_return_sequences=1, temperature=0.7)
            
            return {
                'content': result[0]['generated_text'],
                'method': 'huggingface'
            }
            
        except Exception as e:
            logger.error(f"Hugging Face generation failed: {e}")
            raise e
    
    def _generate_cover_letter_template(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate cover letter using template-based approach"""
        
        template_str = """
Dear Hiring Manager,

I am writing to express my strong interest in the {{ job_title }} position at {{ company }}. With my background in {{ experience_level }} and expertise in {{ key_skills }}, I am excited about the opportunity to contribute to your team.

{% if professional_summary %}
{{ professional_summary }}
{% endif %}

In my previous roles, I have developed strong skills in {{ technical_skills }}, which directly align with the requirements mentioned in your job posting. {% if requirements %}I noticed that you are looking for someone with {{ relevant_requirements }}, and I believe my experience makes me an ideal candidate.{% endif %}

{% if work_experience %}
My relevant experience includes:
{{ formatted_experience }}
{% endif %}

{% if custom_instructions %}
{{ custom_instructions }}
{% endif %}

I am particularly drawn to {{ company }} because of its reputation for {{ company_appeal }}. I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's continued success.

Thank you for considering my application. I look forward to hearing from you.

Sincerely,
{{ full_name }}
"""

        # Prepare context data
        context_data = {
            'job_title': job_posting.get('title', 'this position'),
            'company': job_posting.get('company', 'your organization'),
            'full_name': user_profile.get('full_name', ''),
            'experience_level': user_profile.get('experience_level', '').replace('_', ' '),
            'professional_summary': user_profile.get('professional_summary', ''),
            'technical_skills': self._format_skills_for_template(user_profile.get('technical_skills', '')),
            'key_skills': self._extract_key_skills(user_profile, job_posting),
            'relevant_requirements': self._extract_relevant_requirements(user_profile, job_posting),
            'formatted_experience': self._format_experience_for_template(user_profile.get('work_experience', '')),
            'company_appeal': self._generate_company_appeal(job_posting),
            'custom_instructions': custom_instructions,
        }
        
        template = Template(template_str)
        content = template.render(Context(context_data))
        
        return {
            'content': content.strip(),
            'method': 'template'
        }
    
    def _generate_resume_paid(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate resume using paid APIs"""
        
        # Try OpenAI first
        if hasattr(self, 'openai_client'):
            try:
                return self._generate_resume_openai(user_profile, job_posting, custom_instructions)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        
        # Try Anthropic
        if hasattr(self, 'anthropic_client'):
            try:
                return self._generate_resume_anthropic(user_profile, job_posting, custom_instructions)
            except Exception as e:
                logger.warning(f"Anthropic failed: {e}")
        
        # Fallback to free methods
        return self._generate_resume_free(user_profile, job_posting, custom_instructions)
    
    def _generate_resume_openai(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate resume using OpenAI GPT"""
        
        prompt = self._build_resume_prompt(user_profile, job_posting, custom_instructions)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Create well-structured, ATS-friendly resumes that highlight relevant skills and experience for specific job opportunities."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.6
        )
        
        content = response.choices[0].message.content
        return {
            'content': content,
            'method': 'openai'
        }
    
    def _generate_resume_anthropic(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate resume using Anthropic Claude"""
        
        prompt = self._build_resume_prompt(user_profile, job_posting, custom_instructions)
        
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        return {
            'content': content,
            'method': 'anthropic'
        }
    
    def _generate_resume_free(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate resume using free methods"""
        
        # For resumes, template-based approach works well
        return self._generate_resume_template(user_profile, job_posting, custom_instructions)
    
    def _generate_resume_template(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> Dict:
        """Generate resume using template-based approach"""
        
        template_str = """
{{ full_name }}
{% if email %}{{ email }}{% endif %}{% if phone %} | {{ phone }}{% endif %}{% if location %} | {{ location }}{% endif %}
{% if linkedin_url %}{{ linkedin_url }}{% endif %}{% if portfolio_url %} | {{ portfolio_url }}{% endif %}

{% if professional_summary %}
PROFESSIONAL SUMMARY
{{ professional_summary }}
{% endif %}

TECHNICAL SKILLS
{{ formatted_technical_skills }}

{% if soft_skills %}
CORE COMPETENCIES
{{ formatted_soft_skills }}
{% endif %}

{% if work_experience %}
PROFESSIONAL EXPERIENCE
{{ formatted_work_experience }}
{% endif %}

{% if education %}
EDUCATION
{{ education }}
{% endif %}

{% if certifications %}
CERTIFICATIONS
{{ certifications }}
{% endif %}

{% if achievements %}
KEY ACHIEVEMENTS
{{ achievements }}
{% endif %}
"""

        context_data = {
            'full_name': user_profile.get('full_name', '').upper(),
            'email': user_profile.get('email', ''),
            'phone': user_profile.get('phone', ''),
            'location': user_profile.get('location', ''),
            'linkedin_url': user_profile.get('linkedin_url', ''),
            'portfolio_url': user_profile.get('portfolio_url', ''),
            'professional_summary': self._tailor_summary_for_job(user_profile, job_posting),
            'formatted_technical_skills': self._format_technical_skills_for_resume(user_profile, job_posting),
            'formatted_soft_skills': self._format_soft_skills_for_resume(user_profile.get('soft_skills', '')),
            'formatted_work_experience': self._format_work_experience_for_resume(user_profile.get('work_experience', ''), job_posting),
            'education': user_profile.get('education', ''),
            'certifications': user_profile.get('certifications', ''),
            'achievements': user_profile.get('achievements', ''),
        }
        
        template = Template(template_str)
        content = template.render(Context(context_data))
        
        return {
            'content': content.strip(),
            'method': 'template'
        }
    
    # Helper methods for building prompts
    def _build_cover_letter_prompt(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> str:
        """Build a comprehensive prompt for cover letter generation"""
        
        prompt = f"""
Write a professional cover letter for the following job application:

JOB DETAILS:
- Position: {job_posting.get('title', 'N/A')}
- Company: {job_posting.get('company', 'N/A')}
- Location: {job_posting.get('location', 'N/A')}

JOB REQUIREMENTS:
{job_posting.get('requirements', 'See job description below')}

JOB DESCRIPTION:
{job_posting.get('description', 'N/A')[:1000]}

CANDIDATE PROFILE:
- Name: {user_profile.get('full_name', 'N/A')}
- Experience Level: {user_profile.get('experience_level', 'N/A')}
- Technical Skills: {user_profile.get('technical_skills', 'N/A')}
- Professional Summary: {user_profile.get('professional_summary', 'N/A')}
- Work Experience: {user_profile.get('work_experience', 'N/A')[:500]}

{f"SPECIAL INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

Please write a compelling cover letter that:
1. Shows genuine interest in the position and company
2. Highlights relevant skills and experience that match the job requirements
3. Demonstrates knowledge of the company/role
4. Is professional yet personable
5. Is approximately 3-4 paragraphs long
6. Includes a proper salutation and closing

Cover Letter:
"""
        return prompt
    
    def _build_short_cover_letter_prompt(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> str:
        """Build a shorter prompt for smaller models"""
        
        return f"""
Write a cover letter for {user_profile.get('full_name', 'the candidate')} applying for {job_posting.get('title', 'a position')} at {job_posting.get('company', 'the company')}. 

Skills: {user_profile.get('technical_skills', '')[:200]}
Experience: {user_profile.get('experience_level', '')}

Cover letter:
"""
    
    def _build_resume_prompt(self, user_profile: Dict, job_posting: Dict, custom_instructions: str) -> str:
        """Build a comprehensive prompt for resume generation"""
        
        prompt = f"""
Create a tailored, ATS-friendly resume for the following job application:

TARGET JOB:
- Position: {job_posting.get('title', 'N/A')}
- Company: {job_posting.get('company', 'N/A')}
- Requirements: {job_posting.get('requirements', 'N/A')[:500]}

CANDIDATE INFORMATION:
- Name: {user_profile.get('full_name', 'N/A')}
- Email: {user_profile.get('email', 'N/A')}
- Phone: {user_profile.get('phone', 'N/A')}
- Location: {user_profile.get('location', 'N/A')}
- LinkedIn: {user_profile.get('linkedin_url', 'N/A')}
- Experience Level: {user_profile.get('experience_level', 'N/A')}
- Technical Skills: {user_profile.get('technical_skills', 'N/A')}
- Professional Summary: {user_profile.get('professional_summary', 'N/A')}
- Work Experience: {user_profile.get('work_experience', 'N/A')}
- Education: {user_profile.get('education', 'N/A')}
- Certifications: {user_profile.get('certifications', 'N/A')}
- Achievements: {user_profile.get('achievements', 'N/A')}

{f"SPECIAL INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

Please create a well-structured resume that:
1. Highlights skills and experience most relevant to the target job
2. Uses strong action verbs and quantifiable achievements
3. Is ATS-friendly with clear section headers
4. Optimizes keywords from the job requirements
5. Maintains professional formatting

Resume:
"""
        return prompt
    
    # Helper methods for template-based generation
    def _format_skills_for_template(self, skills_str: str) -> str:
        """Format skills string for template"""
        if not skills_str:
            return "relevant technologies"
        
        skills = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        if len(skills) > 5:
            return ', '.join(skills[:5]) + ', and more'
        return ', '.join(skills)
    
    def _extract_key_skills(self, user_profile: Dict, job_posting: Dict) -> str:
        """Extract key skills that match job requirements"""
        user_skills = user_profile.get('technical_skills', '').lower()
        job_text = (job_posting.get('requirements', '') + ' ' + job_posting.get('description', '')).lower()
        
        if not user_skills:
            return "my technical expertise"
        
        skills_list = [skill.strip() for skill in user_skills.split(',')]
        matching_skills = []
        
        for skill in skills_list:
            if skill.lower() in job_text:
                matching_skills.append(skill)
        
        if matching_skills:
            return ', '.join(matching_skills[:3])
        return ', '.join(skills_list[:3])
    
    def _extract_relevant_requirements(self, user_profile: Dict, job_posting: Dict) -> str:
        """Extract requirements that match user skills"""
        requirements = job_posting.get('requirements', '')
        if not requirements:
            return "the mentioned qualifications"
        
        # Simple extraction - in practice, you'd use more sophisticated NLP
        return requirements[:100] + "..." if len(requirements) > 100 else requirements
    
    def _format_experience_for_template(self, experience_str: str) -> str:
        """Format work experience for template"""
        if not experience_str:
            return ""
        
        lines = experience_str.split('\n')
        formatted_lines = []
        
        for line in lines[:3]:  # Limit to first 3 lines
            if line.strip():
                if not line.startswith('•'):
                    line = f"• {line.strip()}"
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _generate_company_appeal(self, job_posting: Dict) -> str:
        """Generate appealing company description"""
        company = job_posting.get('company', '')
        if not company:
            return "innovation and excellence"
        
        # Simple heuristics - in practice, you might use company research APIs
        generic_appeals = [
            "innovation and excellence",
            "cutting-edge technology and collaborative culture",
            "commitment to quality and customer satisfaction",
            "market leadership and growth opportunities"
        ]
        
        return generic_appeals[hash(company) % len(generic_appeals)]
    
    def _tailor_summary_for_job(self, user_profile: Dict, job_posting: Dict) -> str:
        """Tailor professional summary for specific job"""
        summary = user_profile.get('professional_summary', '')
        if not summary:
            return f"Experienced professional with expertise in {user_profile.get('technical_skills', 'relevant technologies')}"
        
        return summary
    
    def _format_technical_skills_for_resume(self, user_profile: Dict, job_posting: Dict) -> str:
        """Format technical skills for resume, prioritizing job-relevant skills"""
        skills_str = user_profile.get('technical_skills', '')
        if not skills_str:
            return "Please add your technical skills"
        
        skills = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        job_text = (job_posting.get('requirements', '') + ' ' + job_posting.get('description', '')).lower()
        
        # Prioritize skills mentioned in job posting
        priority_skills = []
        other_skills = []
        
        for skill in skills:
            if skill.lower() in job_text:
                priority_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Combine with priority skills first
        all_skills = priority_skills + other_skills
        return ' • '.join(all_skills)
    
    def _format_soft_skills_for_resume(self, soft_skills_str: str) -> str:
        """Format soft skills for resume"""
        if not soft_skills_str:
            return ""
        
        skills = [skill.strip() for skill in soft_skills_str.split(',') if skill.strip()]
        return ' • '.join(skills)
    
    def _format_work_experience_for_resume(self, experience_str: str, job_posting: Dict) -> str:
        """Format work experience for resume"""
        if not experience_str:
            return ""
        
        # Split by double newlines to separate jobs
        jobs = experience_str.split('\n\n')
        formatted_jobs = []
        
        for job in jobs[:3]:  # Limit to 3 most recent jobs
            if job.strip():
                formatted_jobs.append(job.strip())
        
        return '\n\n'.join(formatted_jobs)
