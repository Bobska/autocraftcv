# 🚀 AutoCraftCV Quick Start Guide

Get AutoCraftCV running in 5 minutes!

## Prerequisites
- Python 3.8+ installed
- Git (optional, for cloning)
- Internet connection

## Option 1: Automated Setup (Recommended)

### Windows Users
```batch
# Run the setup script
setup.bat

# Follow the prompts and wait for completion
```

### macOS/Linux Users
```bash
# Make script executable and run
chmod +x setup.sh
./setup.sh

# Follow the prompts and wait for completion
```

## Option 2: Manual Setup

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file (optional for free version)
```

### 4. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### 6. Start Server
```bash
python manage.py runserver
```

## 🌐 Access the Application

Open your browser and go to:
- **Main App**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin

## 🧪 Test the Setup

Run the test script to verify everything works:
```bash
python test_setup.py
```

## 📋 First Steps

1. **Free Version** (works immediately):
   - Paste a job URL (LinkedIn, Indeed, etc.)
   - Upload your resume or enter profile manually
   - Generate tailored documents
   - Download PDF/Word files

2. **Paid Version** (requires API keys):
   - Edit `.env` file with your API keys
   - Set `APP_VERSION=paid`
   - Restart the server
   - Enjoy enhanced accuracy and speed

## 🔑 API Keys for Paid Version

Get API keys from:
- **OpenAI**: https://platform.openai.com/
- **Anthropic**: https://console.anthropic.com/
- **ScrapingBee**: https://www.scrapingbee.com/
- **Affinda**: https://www.affinda.com/

Add them to your `.env` file:
```bash
APP_VERSION=paid
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
# ... other keys as needed
```

## 🆘 Need Help?

- **Errors during setup**: Check the troubleshooting section in README.md
- **Import errors**: Make sure virtual environment is activated
- **Database issues**: Run `python manage.py migrate`
- **Template errors**: Ensure all files were created correctly

## 💡 Tips

- **Start with free version**: Test functionality before getting API keys
- **Use test URLs**: Try with publicly accessible job postings
- **Check file formats**: Upload PDF or DOCX resumes (max 10MB)
- **Browser compatibility**: Works best with modern browsers

## 🎯 Example Workflow

1. Go to http://127.0.0.1:8000
2. Paste job URL: `https://www.linkedin.com/jobs/view/123456789`
3. Upload your resume PDF
4. Review extracted information
5. Generate cover letter and tailored resume
6. Download documents
7. Apply for the job!

## 📞 Support

If you encounter issues:
1. Check README.md troubleshooting section
2. Run the test script: `python test_setup.py`
3. Check Django logs for detailed error messages
4. Ensure all dependencies are properly installed

Happy job hunting! 🎉
