# Frameio Project
# startup_env\Scripts\activate
# cd backend; python manage.py runserver
# cd frontend; npm run dev

A full-stack application built with Django backend and Next.js frontend, featuring AI-powered poster/catalog/logo generation.

## 🏗️ Architecture

- **Backend**: Django with Django REST Framework
- **Frontend**: Next.js with TypeScript, Tailwind CSS, and Shadcn UI
- **Database**: MySQL
- **Authentication**: Clerk
- **API Protection**: Arcjet
- **AI Service**: NanoBanana API
- **Testing**: Pytest (backend), Jest (frontend)

## 📱 Social Media Sharing

### Facebook Sharing Fix

Facebook sharing now works correctly with automatic ngrok detection and fallback methods:

#### Option 1: With ngrok (Requires Free Account)
1. **Sign up for ngrok account:**
   - Go to: https://dashboard.ngrok.com/signup
   - Create a free account

2. **Get your authtoken:**
   - Go to: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken

3. **Configure ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
   ```

4. **Start ngrok:**
   ```bash
   ngrok http 3000
   ```

#### Option 2: With Cloudflare Tunnel (No Account Required - Recommended)
1. **Start Cloudflare Tunnel:**
   ```bash
   node start-cloudflare-tunnel.js
   # OR manually: cloudflared tunnel --url http://localhost:3000
   ```

2. **Generate and share posters** - Facebook will automatically use the tunnel URL for rich previews

#### Option 3: Without Tunnel (Fallback Method)
- Facebook sharing will automatically copy content to clipboard for manual sharing
- Other platforms (Twitter, WhatsApp, Email) work normally

#### Testing Facebook Sharing
Open `facebook-sharing-fix-test.html` in your browser to test the sharing functionality.

### Supported Platforms
- ✅ **Facebook** - Rich previews with ngrok, clipboard fallback without
- ✅ **Twitter** - Direct sharing with URLs
- ✅ **WhatsApp** - Direct sharing with URLs  
- ✅ **Email** - Direct sharing with URLs
- ✅ **Instagram** - Clipboard copy (no direct API)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- MySQL 8.0+ (Required)
- Git

### MySQL Setup

Before running the application, you need to set up MySQL:

#### Windows:
1. Download and install MySQL 8.0+ from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
2. During installation, set a root password (remember this!)
3. Start MySQL service: `net start MySQL80`

#### macOS:
```bash
# Install via Homebrew
brew install mysql@8.0
brew services start mysql@8.0

# Secure your installation
mysql_secure_installation
```

#### Linux (Ubuntu/Debian):
```bash
# Install MySQL
sudo apt update
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure your installation
sudo mysql_secure_installation
```

#### Create Database:
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional, for better security)
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Environment Setup

1. **Activate the virtual environment:**
   ```bash
   # Windows
   startup_env\Scripts\activate
   
   # macOS/Linux
   source startup_env/bin/activate
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Configuration

1. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Update the `.env` file with your actual API keys and database credentials:
   - `DB_NAME` - Database name (default: frameio_db)
   - `DB_USER` - MySQL username (default: root)
   - `DB_PASSWORD` - Your MySQL password
   - `DB_HOST` - Database host (default: localhost)
   - `DB_PORT` - MySQL port (default: 3306)
   - `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` from Clerk dashboard
   - `ARCJET_KEY` from Arcjet dashboard
   - `GEMINI_API_KEY` from Google AI Studio [[memory:10031716]]
   - `SECRET_KEY` - generate a secure Django secret key

2. **Set up the database:**
   ```bash
   cd backend
   python manage.py migrate
   python manage.py createsuperuser
   cd ..
   ```

### Running the Application

#### Backend (Django)
```bash
# Activate virtual environment
startup_env\Scripts\activate  # Windows
# source startup_env/bin/activate  # macOS/Linux

# Navigate to backend
cd backend

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```
Backend will be available at: http://localhost:8000

#### Frontend (Next.js)
```bash
# In a new terminal, navigate to frontend
cd frontend

# Start the development server
npm run dev
```
Frontend will be available at: http://localhost:3000

### Testing

#### Backend Testing
```bash
# Activate virtual environment
startup_env\Scripts\activate  # Windows
# source startup_env/bin/activate  # macOS/Linux

# Navigate to backend
cd backend

# Run tests
pytest
```

#### Frontend Testing
```bash
# Navigate to frontend
cd frontend

# Run tests
npm test
```

## 📁 Project Structure

```
Frameio/
├── startup_env/              # Python virtual environment
├── backend/                  # Django backend
│   ├── frameio_backend/     # Django project settings
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # Next.js frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── next.config.js
├── .env                     # Environment variables
├── .gitignore
└── README.md
```

## 🔧 Development Tools

### Backend Dependencies
- Django 5.2.6
- Django REST Framework 3.16.1
- MySQL Client 2.2.7 (MySQL database driver)
- Google Generative AI SDK
- Clerk SDK 0.3.7
- Arcjet 0.0.1
- Pillow 11.3.0
- Redis & Django-Redis (caching)
- Celery (background tasks)
- Pytest 8.4.2
- Pytest-Django 4.11.1

### Frontend Dependencies
- Next.js 15.x
- React 18.x
- TypeScript 5.x
- Tailwind CSS 4.x
- Shadcn UI
- Clerk React SDK
- Axios
- Jest (testing)

## 🚀 Deployment

### Full-Stack Server Deployment (AWS EC2)

For comprehensive server deployment structure and step-by-step guide, see:
- **📋 Full Deployment Structure:** [`deployment/FULL_STACK_DEPLOYMENT_STRUCTURE.md`](deployment/FULL_STACK_DEPLOYMENT_STRUCTURE.md)
- **🚀 Quick Start:** [`deployment/QUICK_START.md`](deployment/QUICK_START.md)
- **📖 Step-by-Step Guide:** [`deployment/STEP_BY_STEP_DEPLOYMENT.md`](deployment/STEP_BY_STEP_DEPLOYMENT.md)
- **📚 Complete Documentation:** [`deployment/README.md`](deployment/README.md)

**Quick Overview:**
- **Backend:** Django + Gunicorn + Nginx on AWS EC2
- **Frontend:** Next.js (can be deployed separately on Vercel or same server)
- **Database:** MySQL 8.0+ on EC2 or cloud service
- **Cache:** Redis (optional)
- **Server IP:** 13.213.53.199

### Alternative Deployment Options

#### Backend Deployment (Railway/Render)
1. Connect your GitHub repository
2. Set environment variables in deployment platform
3. Configure build command: `pip install -r requirements.txt`
4. Set start command: `python manage.py runserver 0.0.0.0:$PORT`

#### Frontend Deployment (Vercel)
1. Connect your GitHub repository
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

#### Database (MySQL Cloud - PlanetScale/AWS RDS/DigitalOcean)
1. Create MySQL 8.0+ database instance
2. Update database credentials in environment variables:
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
3. Ensure MySQL connection allows remote connections
4. Run migrations: `python manage.py migrate`

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_NAME` | MySQL database name | Yes |
| `DB_USER` | MySQL username | Yes |
| `DB_PASSWORD` | MySQL password | Yes |
| `DB_HOST` | MySQL host (localhost/cloud) | Yes |
| `DB_PORT` | MySQL port (default: 3306) | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `CLERK_PUBLISHABLE_KEY` | Clerk public key | Yes |
| `CLERK_SECRET_KEY` | Clerk secret key | Yes |
| `ARCJET_KEY` | Arcjet API key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `REDIS_URL` | Redis connection URL | Optional |

## 📝 API Documentation

The API documentation will be available at `/api/docs/` when the backend is running.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
