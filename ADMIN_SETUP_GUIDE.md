# Admin Dashboard - Quick Setup Guide

## 🎯 What Was Built

A complete, secure admin dashboard with:

- ✅ Custom username/password authentication (separate from user auth)
- ✅ Protected admin routes with middleware
- ✅ Dashboard overview with stats and charts
- ✅ Users management page
- ✅ Analytics page with Google Analytics placeholder
- ✅ Settings page with theme toggle
- ✅ Beautiful, responsive UI with ShadCN components
- ✅ Session management with JWT tokens
- ✅ Dark/Light mode support

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
cd frontend
npm install jose
```

### 2. Create Environment File

Create `frontend/.env.local`:

```env
ADMIN_USERNAME=tsg_admin
ADMIN_PASSWORD=tsgtharsiyanshahastragautham321
ADMIN_JWT_SECRET=your-super-secret-jwt-key-change-in-production-12345678
ADMIN_SESSION_EXPIRY=24
```

**OR** run the setup script:

```bash
cd frontend
node setup-admin.js
```

### 3. Start the Server

```bash
npm run dev
```

## 🔐 Access Admin Dashboard

1. Navigate to: **http://localhost:3000/admin/login**
2. Login with:
   - **Username**: `tsg_admin`
   - **Password**: `tsgtharsiyanshahastragautham321`

## 📁 What's Included

### Pages

- `/admin/login` - Admin login page
- `/admin` - Dashboard overview
- `/admin/users` - Users management
- `/admin/analytics` - Analytics & metrics
- `/admin/settings` - Admin settings

### Components

- `Sidebar` - Navigation sidebar
- `Navbar` - Top navigation bar
- `StatsCard` - Metric display cards
- `UserTable` - User management table
- `AnalyticsChart` - Data visualization

### API Routes

- `POST /api/admin/login` - Admin login
- `POST /api/admin/logout` - Admin logout
- `GET /api/admin/verify` - Verify session

## 🔒 Security Features

- ✅ httpOnly cookies (XSS protection)
- ✅ JWT token validation
- ✅ 24-hour session expiry
- ✅ Middleware route protection
- ✅ Secure flag in production
- ✅ Path-scoped cookies

## 🎨 Features

### Dashboard Overview
- Total users count with trends
- AI posts generated statistics
- Active companies metrics
- Recent activity feed
- Popular aspect ratios chart
- Most active companies visualization

### Users Management
- Complete user list with search
- User status indicators
- Action buttons (View, Edit, Delete)
- Pagination support
- Export functionality

### Analytics
- Revenue metrics
- Page views tracking
- Conversion rates
- User growth charts
- Post generation trends
- Feature usage statistics
- Device breakdown
- Google Analytics integration placeholder

### Settings
- Admin profile management
- Password change functionality
- Dark/Light theme toggle
- Notification preferences
- Email alerts configuration

## 📋 Files Created

```
frontend/
├── .env.local (you need to create this)
├── setup-admin.js
├── ADMIN_DASHBOARD_README.md
│
├── src/
│   ├── app/
│   │   ├── admin/
│   │   │   ├── login/
│   │   │   │   ├── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── users/
│   │   │   │   ├── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── analytics/
│   │   │   │   ├── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── settings/
│   │   │   │   ├── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx
│   │   │
│   │   └── api/
│   │       └── admin/
│   │           ├── login/route.ts
│   │           ├── logout/route.ts
│   │           └── verify/route.ts
│   │
│   ├── components/
│   │   ├── admin/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   ├── UserTable.tsx
│   │   │   └── AnalyticsChart.tsx
│   │   │
│   │   └── ui/
│   │       └── table.tsx (updated)
│   │
│   ├── contexts/
│   │   └── admin-auth-context.tsx
│   │
│   ├── lib/
│   │   └── admin-auth.ts
│   │
│   └── middleware.ts (updated)
```

## ⚠️ Important Notes

### 1. User Authentication (Clerk) is NOT Affected

The admin dashboard is **completely separate** from user authentication. Users still log in with Clerk as before.

### 2. Change Credentials in Production

**CRITICAL**: Before deploying to production, change:

```env
ADMIN_USERNAME=your_secure_username
ADMIN_PASSWORD=your_very_strong_password
ADMIN_JWT_SECRET=generate_a_new_secret_key
```

Generate a secure JWT secret:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 3. Dependencies Required

You MUST install `jose` for JWT handling:
```bash
npm install jose
```

## 🧪 Testing

### Login Test
1. Go to http://localhost:3000/admin/login
2. Enter credentials
3. Should redirect to dashboard

### Protection Test
1. Try accessing http://localhost:3000/admin without logging in
2. Should redirect to login page

### Logout Test
1. Click logout in sidebar
2. Should clear session and redirect to login

### Session Persistence
1. Login to admin
2. Refresh page
3. Should stay logged in

## 🎯 Next Steps

### Connect Real Data

Replace mock data with API calls:

```tsx
// Example: In /admin/users/page.tsx
useEffect(() => {
  async function fetchUsers() {
    const res = await fetch('http://localhost:8000/api/admin/users');
    const data = await res.json();
    setUsers(data);
  }
  fetchUsers();
}, []);
```

### Add Google Analytics

1. Install package: `npm install react-ga4`
2. Add tracking ID to `.env.local`
3. Initialize in admin layout

### Enhance Security

- Add rate limiting to login endpoint
- Implement audit logging
- Add two-factor authentication
- Set up alerts for failed login attempts

## 📖 Full Documentation

See `frontend/ADMIN_DASHBOARD_README.md` for complete documentation including:
- Architecture details
- Security best practices
- Customization guide
- Troubleshooting
- Future enhancements

## 🆘 Troubleshooting

### Can't Login
- Check .env.local exists with correct credentials
- Verify jose is installed: `npm list jose`
- Check browser console for errors

### Pages Not Loading
- Ensure middleware.ts is properly configured
- Check admin-auth.ts has no errors
- Verify cookies are enabled in browser

### Styling Issues
- Ensure TailwindCSS is properly configured
- Check ShadCN components are installed
- Verify globals.css is imported

## ✨ Summary

You now have a fully functional admin dashboard with:

- 🔐 Custom authentication
- 📊 Dashboard with metrics
- 👥 User management
- 📈 Analytics & charts
- ⚙️ Settings & preferences
- 🎨 Modern, responsive UI
- 🔒 Secure session management

**Access**: http://localhost:3000/admin/login

**Credentials**:
- Username: `tsg_admin`
- Password: `tsgtharsiyanshahastragautham321`

---

Built with ❤️ using Next.js, TypeScript, TailwindCSS, and ShadCN UI

