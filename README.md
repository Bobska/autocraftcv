# AutoCraftCV - AI-Powered Resume & Cover Letter Generator

AutoCraftCV is a Django web application that helps job seekers create tailored cover letters and resumes based on job advertisements. It offers both free (open-source tools) and paid (premium APIs) versions for different accuracy and speed requirements.

## Features

### Core Functionality
- **Job Advertisement Processing**: Scrape and parse job postings from URLs (LinkedIn, Indeed, etc.)
- **Resume Parsing**: Upload PDF/DOCX resumes with automatic content extraction
- **Manual Profile Entry**: Web forms for entering professional information
- **AI Content Generation**: Create tailored cover letters and resumes
- **Document Export**: Download generated documents in PDF and Word formats

### Free Version Features
- **Job Scraping**: BeautifulSoup4 + Selenium for web scraping
- **Resume Parsing**: pdfplumber, PyMuPDF, python-docx for file processing
- **AI Generation**: Hugging Face Transformers, Ollama local models, template-based fallbacks
- **Document Generation**: reportlab (PDF) and python-docx (Word) export

### Paid Version Features
- **Enhanced Scraping**: ScrapingBee API, Diffbot API for reliable data extraction
- **Professional Parsing**: Affinda Resume Parser API, RChilli parsing service
- **Premium AI**: OpenAI GPT-4, Anthropic Claude for superior content quality
- **Same Export Options**: PDF and Word document generation

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd autocraftcv
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# For free version, you only need to set:
# SECRET_KEY=your-secret-key-here
# DEBUG=True
# APP_VERSION=free
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 6. Static Files
```bash
python manage.py collectstatic
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## Configuration

### Free Version Setup
The free version works out of the box with no additional configuration required. It uses:
- Local web scraping tools
- Open-source resume parsing libraries
- Template-based or local AI model generation

### Paid Version Setup
To use the paid version with premium APIs, set the following in your `.env` file:

```bash
APP_VERSION=paid

# Required for AI content generation
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Optional for enhanced scraping
SCRAPINGBEE_API_KEY=your-scrapingbee-api-key-here
DIFFBOT_API_KEY=your-diffbot-api-key-here

# Optional for professional resume parsing
AFFINDA_API_KEY=your-affinda-api-key-here
```

### API Key Sources
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)
- **ScrapingBee**: Get API key from [ScrapingBee](https://www.scrapingbee.com/)
- **Diffbot**: Get API key from [Diffbot](https://www.diffbot.com/)
- **Affinda**: Get API key from [Affinda](https://www.affinda.com/)

## Usage Guide

### 1. Job URL Processing
1. Paste a job posting URL from supported sites (LinkedIn, Indeed, Glassdoor, company career pages)
2. The system will scrape and extract job details, requirements, and qualifications
3. Review the extracted information

### 2. Profile Creation
Choose one of two methods:

**Option A: Upload Resume**
1. Upload your PDF or Word resume (max 10MB)
2. The system will parse and extract your information
3. Review and edit the extracted data

**Option B: Manual Entry**
1. Fill out the comprehensive profile form
2. Include personal info, skills, experience, education, and achievements
3. Save your profile

### 3. Document Generation
1. Select document type (cover letter, resume, or both)
2. Choose output format (PDF, Word, or both)
3. Add any custom instructions
4. Generate and download your documents

### 4. Download & Use
1. Review generated documents
2. Download in your preferred format
3. Customize further if needed
4. Submit with your job applications

## Testing

### Sample Job URLs for Testing
- LinkedIn: https://www.linkedin.com/jobs/view/[job-id]
- Indeed: https://www.indeed.com/viewjob?jk=[job-key]
- Company career pages (most are supported)

### Test Resume Files
Upload PDF or Word resume files to test the parsing functionality.

### Testing Both Versions
1. Start with free version (APP_VERSION=free)
2. Test all functionality
3. Switch to paid version (APP_VERSION=paid) after setting up API keys
4. Compare quality and speed differences

## Architecture

### Project Structure
```
autocraftcv/
├── autocraftcv/           # Django project settings
├── jobassistant/          # Main application
│   ├── models.py          # Database models
│   ├── views.py           # Request handlers
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin interface
│   └── services/          # Business logic
│       ├── scraping_service.py
│       ├── parsing_service.py
│       ├── content_generation_service.py
│       └── document_generation_service.py
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploads
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Key Components

#### Models
- `JobPosting`: Stores scraped job information
- `UserProfile`: User professional information
- `GeneratedDocument`: Generated cover letters and resumes
- `ScrapingSession`: Tracks scraping operations
- `AppSettings`: Application configuration

#### Services
- `JobScrapingService`: Web scraping with free/paid options
- `ResumeParsingService`: File parsing with free/paid options
- `ContentGenerationService`: AI content generation
- `DocumentGenerationService`: PDF/Word document creation

## Deployment

### Production Considerations
1. **Security**: Set `DEBUG=False`, use strong `SECRET_KEY`
2. **Database**: Use PostgreSQL or MySQL instead of SQLite
3. **Static Files**: Configure proper static file serving
4. **Media Files**: Set up proper file storage (AWS S3, etc.)
5. **Environment Variables**: Use proper secret management
6. **HTTPS**: Ensure SSL/TLS encryption
7. **Monitoring**: Add logging and error tracking

### Docker Deployment (Optional)
```dockerfile
# Example Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Troubleshooting

### Common Issues

**1. Scraping Failures**
- Check if the job URL is publicly accessible
- Some sites may require the paid APIs for reliable scraping
- Verify your internet connection

**2. Resume Parsing Issues**
- Ensure file is PDF or Word format
- File size must be under 10MB
- Try a different file format if parsing fails

**3. AI Generation Problems**
- For free version: Check if Ollama is installed and running
- For paid version: Verify API keys are correct and have sufficient credits
- Check your internet connection for API calls

**4. Download Issues**
- Check browser download settings
- Ensure sufficient disk space
- Try right-click "Save As" if auto-download fails

### Error Messages

**"Could not extract job information"**
- The job URL may not be supported
- Try the manual profile entry option
- Switch to paid version for better scraping

**"Error parsing resume"**
- File may be corrupted or in unsupported format
- Try converting to PDF or Word format
- Use manual entry as alternative

**"API key not found"**
- Check your .env file configuration
- Ensure API keys are properly set
- Verify API key validity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

For support and questions:
1. Check this README for common solutions
2. Review the troubleshooting section
3. Submit an issue on the repository
4. Check the Django documentation for framework-specific questions

## Version History

- **v1.0.0**: Initial release with free and paid versions
- Features: Job scraping, resume parsing, AI generation, document export
- Support for multiple job sites and document formats

## Future Enhancements

- **Multi-language support**: Generate documents in different languages
- **Job matching**: AI-powered job recommendation system
- **Interview prep**: Generate interview questions and answers
- **Portfolio generation**: Create professional portfolio websites
- **Team collaboration**: Multiple user support and document sharing
- **Advanced analytics**: Track application success rates
- **Mobile app**: iOS and Android applications
- **Browser extension**: Quick generation from job sites
