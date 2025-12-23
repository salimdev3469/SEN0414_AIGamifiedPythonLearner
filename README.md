# 🐍 Gamified Python Learner AI

> An interactive, AI-powered Python learning platform with gamification mechanics.

## 📋 Project Overview

This is a Django-based web application that transforms learning Python into an engaging, personalized experience through:
- 🤖 **AI Tutor** powered by Google Gemini
- 🎮 **Gamification** with XP, levels, and badges
- 💻 **Interactive Coding** with real-time feedback
- 📚 **Structured Curriculum** from beginner to advanced

## 🏗️ Project Structure

```
porje/
├── apps/                      # Django applications
│   ├── authentication/        # User management & auth
│   ├── learning/             # Curriculum & lessons
│   ├── coding/               # Code execution & exercises
│   ├── gamification/         # XP, levels, badges
│   └── ai_tutor/             # AI assistance integration
├── config/                    # Project settings
├── static/                    # CSS, JS, images
├── templates/                 # HTML templates
├── media/                     # User uploads
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Links

### 🌐 Want to Try it LIVE?
**Deploy in 5 minutes!** → See [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md)

### 💻 Local Development
Follow the installation steps below.

---

## 📦 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite for development)
- Google Gemini API Key ([Get it free](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Porje
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

GEMINI_API_KEY=your-gemini-api-key
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

## 📦 Technology Stack

- **Backend**: Django 5.0.1
- **Database**: PostgreSQL / SQLite
- **AI**: Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript
- **Code Execution**: Secure subprocess isolation

## 🎯 Features Roadmap

### Phase 1: Foundation ✅
- [x] Project setup
- [x] Django apps structure
- [x] Settings configuration

### Phase 2: Authentication (In Progress)
- [ ] User registration
- [ ] Login/Logout
- [ ] Password reset
- [ ] User profile

### Phase 3: Learning Content
- [ ] Module & lesson models
- [ ] Curriculum display
- [ ] Lesson viewer
- [ ] Progress tracking

### Phase 4: Interactive Coding
- [ ] Code editor integration
- [ ] Secure code execution
- [ ] Test case evaluation
- [ ] Submission history

### Phase 5: Gamification
- [ ] XP system
- [ ] Level progression
- [ ] Badge awards
- [ ] Leaderboard

### Phase 6: AI Tutor
- [ ] Gemini API integration
- [ ] Error explanations
- [ ] Hint generation
- [ ] Concept clarification

### Phase 7: Polish & Deploy ✅
- [x] UI/UX improvements
- [x] Testing
- [x] Security hardening
- [x] Production deployment ready

## 🌍 Deployment

### Quick Deploy (5 minutes)
See **[DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md)** for fastest deployment to Render (free).

### Detailed Deployment Guide
See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for:
- Render (Recommended)
- PythonAnywhere
- Railway
- Custom VPS

**Platforms:**
- ✅ **Render**: Fully automated, free tier, PostgreSQL
- ✅ **PythonAnywhere**: Django-optimized, easy setup
- ✅ **Railway**: Modern, GitHub integration

## 🔐 Security Features

- Password hashing with Django's built-in system
- CSRF protection
- Sandboxed code execution with resource limits
- XSS prevention
- SQL injection protection

## 📚 API Endpoints (To Be Implemented)

```
/auth/register/              - User registration
/auth/login/                 - User login
/auth/logout/                - User logout
/dashboard/                  - User dashboard
/curriculum/                 - View all modules
/lesson/<id>/                - View specific lesson
/exercise/<id>/              - Code exercise
/api/exercise/<id>/submit/   - Submit code
/api/ai/get-feedback/        - AI tutor assistance
/profile/                    - User profile
```

## 🤝 Contributing

This is a learning project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 👥 Target Personas

- **Alex (Beginner)**: 20-year-old student, no coding experience
- **Maria (Career Changer)**: 32-year-old professional transitioning to tech

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ for Python learners everywhere**
