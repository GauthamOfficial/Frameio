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
- MySQL 8.0+
- Git

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
   - `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` from Clerk dashboard
   - `ARCJET_API_KEY` from Arcjet dashboard
   - `NANOBANANA_API_KEY` from NanoBanana API
   - `DATABASE_URL` with your MySQL connection string
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
- MySQL Client 2.2.7
- Clerk SDK 0.3.7
- Arcjet 0.0.1
- Pillow 11.3.0
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

### Backend Deployment (Railway/Render)
1. Connect your GitHub repository
2. Set environment variables in deployment platform
3. Configure build command: `pip install -r requirements.txt`
4. Set start command: `python manage.py runserver 0.0.0.0:$PORT`

### Frontend Deployment (Vercel)
1. Connect your GitHub repository
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Database (Neon/MySQL Cloud)
1. Create database instance
2. Update `DATABASE_URL` in environment variables
3. Run migrations in production

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | MySQL connection string | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `CLERK_PUBLISHABLE_KEY` | Clerk public key | Yes |
| `CLERK_SECRET_KEY` | Clerk secret key | Yes |
| `ARCJET_API_KEY` | Arcjet API key | Yes |
| `NANOBANANA_API_KEY` | NanoBanana API key | Yes |

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
