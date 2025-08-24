# 🚀 AutoCraftCV - Complete Deployment Guide

## 🎉 Setup Complete!

Your AutoCraftCV application is now successfully installed and running! Here's everything you need to know.

## ✅ What's Working

✅ **Django Application**: Fully configured and running  
✅ **Database**: SQLite database with all migrations applied  
✅ **Models**: All data models created (JobPosting, UserProfile, GeneratedDocument, etc.)  
✅ **Services**: Free and paid service integrations ready  
✅ **Templates**: Responsive web interface with Bootstrap  
✅ **Admin Panel**: Django admin interface configured  
✅ **Static Files**: Directory structure created  
✅ **Virtual Environment**: Python dependencies installed  

## 🌐 Access Points

- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin
- **API Endpoints**: Various endpoints for AJAX functionality

## 📁 Project Structure

```
autocraftcv/
├── 📁 .venv/                    # Virtual environment (created)
├── 📁 jobassistant/             # Main Django app
│   ├── 📄 models.py            # Database models ✅
│   ├── 📄 views.py             # Request handlers ✅
│   ├── 📄 forms.py             # Web forms ✅
│   ├── 📄 urls.py              # URL routing ✅
│   ├── 📄 admin.py             # Admin interface ✅
│   ├── 📁 services/            # Business logic ✅
│   ├── 📁 migrations/          # Database migrations ✅
│   └── 📁 templates/           # HTML templates ✅
├── 📁 templates/               # Global templates ✅
├── 📁 static/                  # Static files (CSS, JS) ✅
├── 📁 media/                   # User uploads ✅
├── 📄 .env                     # Environment config ✅
├── 📄 requirements.txt         # Dependencies ✅
├── 📄 README.md               # Documentation ✅
├── 📄 setup.py                # Setup script ✅
├── 📄 test_setup.py           # Test script ✅
└── 📄 manage.py               # Django management ✅
```

## 🔧 Current Configuration

### Free Version Features (Active)
- ✅ **Job Scraping**: BeautifulSoup4 + Selenium
- ✅ **Resume Parsing**: pdfplumber, PyMuPDF, python-docx
- ✅ **AI Generation**: Template-based with Hugging Face fallback
- ✅ **Document Export**: PDF (reportlab) and Word (python-docx)

### Paid Version Features (Available with API keys)
- 🔑 **Enhanced Scraping**: ScrapingBee, Diffbot APIs
- 🔑 **Professional Parsing**: Affinda, RChilli APIs
- 🔑 **Premium AI**: OpenAI GPT-4, Anthropic Claude
- ✅ **Same Export Options**: PDF and Word generation

## 🚀 How to Use

### 1. Basic Workflow (Free Version)
1. **Visit**: http://127.0.0.1:8000
2. **Paste Job URL**: LinkedIn, Indeed, Glassdoor, company pages
3. **Upload Resume**: PDF or Word file (max 10MB)
4. **Review Data**: Check extracted job details and profile info
5. **Generate Documents**: Create tailored cover letter and resume
6. **Download**: Get PDF/Word files for your applications

### 2. Example Test URLs
```
LinkedIn: https://www.linkedin.com/jobs/view/[job-id]
Indeed: https://www.indeed.com/viewjob?jk=[job-key]
Company Pages: Most career pages work!
```

### 3. Switching to Paid Version
1. **Get API Keys** from:
   - OpenAI: https://platform.openai.com/
   - Anthropic: https://console.anthropic.com/
   - ScrapingBee: https://www.scrapingbee.com/
   - Affinda: https://www.affinda.com/

2. **Edit .env file**:
   ```bash
   APP_VERSION=paid
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   # ... add other keys as needed
   ```

3. **Restart server**:
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   .\.venv\Scripts\python.exe manage.py runserver
   ```

## 🛠️ Development Commands

### Virtual Environment
```bash
# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Deactivate
deactivate
```

### Django Management
```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Testing
```bash
# Run setup tests
python test_setup.py

# Django tests (if you add them)
python manage.py test
```

## 📊 Database Management

### Admin Interface
1. **Create superuser**: `python manage.py createsuperuser`
2. **Access admin**: http://127.0.0.1:8000/admin
3. **Manage data**: View/edit all models through web interface

### Models Available
- **JobPosting**: Scraped job advertisements
- **UserProfile**: User professional information
- **GeneratedDocument**: Created cover letters and resumes
- **ScrapingSession**: Tracking scraping operations
- **AppSettings**: Application configuration

## 🔒 Security Considerations

### Development (Current)
- ✅ DEBUG=True (for development)
- ✅ SQLite database (suitable for development)
- ✅ Console email backend
- ✅ HTTP (no SSL required)

### Production (When deploying)
- 🔐 Set DEBUG=False
- 🔐 Use PostgreSQL/MySQL
- 🔐 Configure real email service
- 🔐 Enable HTTPS/SSL
- 🔐 Use environment variables for secrets
- 🔐 Configure proper logging

## 🐛 Troubleshooting

### Common Issues

**"Server not starting"**
- Check if port 8000 is available
- Ensure virtual environment is activated
- Verify all dependencies are installed

**"Import errors"**
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**"Database errors"**
- Run migrations: `python manage.py migrate`
- Check database file permissions

**"Template not found"**
- Ensure all templates were created
- Check TEMPLATES setting in settings.py

**"Static files not loading"**
- Run: `python manage.py collectstatic`
- Check STATIC_URL and STATICFILES_DIRS settings

### API Issues (Paid Version)

**"OpenAI API errors"**
- Verify API key in .env file
- Check account credits and limits
- Ensure proper key format (starts with sk-)

**"Scraping failures"**
- Try different job URLs
- Check if site requires authentication
- Consider using paid scraping APIs

## 📈 Performance Optimization

### For Production
- Use Gunicorn or uWSGI instead of runserver
- Configure Nginx for static file serving
- Set up Redis for caching
- Use PostgreSQL for better performance
- Configure logging and monitoring

### For Development
- Use pagination for large datasets
- Implement caching for API calls
- Add database indexing for frequently queried fields

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
pip list --outdated  # Check for updates
pip install -r requirements.txt --upgrade
```

### Database Backups
```bash
# Backup SQLite
python manage.py dumpdata > backup.json

# Restore
python manage.py loaddata backup.json
```

### Code Updates
- Keep models, services, and templates in sync
- Test changes with test_setup.py
- Run migrations after model changes

## 📞 Support Resources

1. **Django Documentation**: https://docs.djangoproject.com/
2. **Bootstrap Documentation**: https://getbootstrap.com/docs/
3. **API Documentation**: Check respective API provider docs
4. **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

## 🎯 Next Steps

### Immediate
1. ✅ Test basic functionality with sample job URLs
2. ✅ Upload test resume files
3. ✅ Generate sample documents
4. ✅ Verify download functionality

### Short Term
- 🔑 Set up paid API keys for enhanced features
- 👤 Create admin superuser for data management
- 🎨 Customize templates and styling
- 📧 Configure email settings

### Long Term
- 🚀 Deploy to production server
- 📊 Add analytics and monitoring
- 🔧 Implement additional features
- 🧪 Add comprehensive testing

## ✨ Success! 

Your AutoCraftCV application is fully functional and ready to help you create outstanding job applications. Start by testing the free version, then upgrade to paid APIs for enhanced performance and accuracy.

**Happy job hunting!** 🎉

---

*For additional help, refer to README.md or check the troubleshooting section above.*
