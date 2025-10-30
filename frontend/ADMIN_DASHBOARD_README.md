# Admin Dashboard Documentation

## Overview

A secure, standalone admin dashboard built with Next.js 15, TypeScript, TailwindCSS, and ShadCN UI. Features custom username/password authentication independent from user authentication.

## 🔐 Authentication

### Credentials

The admin credentials are stored in `.env.local`:

```env
ADMIN_USERNAME=tsg_admin
ADMIN_PASSWORD=tsgtharsiyanshahastragautham321
ADMIN_JWT_SECRET=your-super-secret-jwt-key-change-in-production-12345678
ADMIN_SESSION_EXPIRY=24
```

### How It Works

1. **Login**: Admin enters credentials at `/admin/login`
2. **Session**: JWT token stored in httpOnly cookie with 24-hour expiry
3. **Protection**: Middleware checks for valid session on all `/admin/*` routes
4. **Logout**: Clears session cookie and redirects to login

### Security Features

- httpOnly cookies prevent XSS attacks
- Secure flag enabled in production
- JWT token validation with expiry
- Path-scoped cookies (`/admin` only)
- Middleware-level route protection

## 📁 File Structure

```
frontend/src/
├── app/
│   ├── admin/
│   │   ├── login/
│   │   │   ├── page.tsx           # Login page
│   │   │   └── layout.tsx         # Login layout wrapper
│   │   ├── users/
│   │   │   ├── page.tsx           # Users management
│   │   │   └── loading.tsx        # Loading state
│   │   ├── analytics/
│   │   │   ├── page.tsx           # Analytics dashboard
│   │   │   └── loading.tsx        # Loading state
│   │   ├── settings/
│   │   │   ├── page.tsx           # Admin settings
│   │   │   └── loading.tsx        # Loading state
│   │   ├── layout.tsx             # Main admin layout
│   │   ├── page.tsx               # Dashboard overview
│   │   ├── loading.tsx            # Loading state
│   │   └── error.tsx              # Error boundary
│   └── api/
│       └── admin/
│           ├── login/route.ts     # Login API
│           ├── logout/route.ts    # Logout API
│           └── verify/route.ts    # Session verification
├── components/
│   └── admin/
│       ├── Sidebar.tsx            # Navigation sidebar
│       ├── Navbar.tsx             # Top navbar
│       ├── StatsCard.tsx          # Stat display card
│       ├── UserTable.tsx          # User management table
│       └── AnalyticsChart.tsx     # Chart component
├── contexts/
│   └── admin-auth-context.tsx     # Auth context & hooks
├── lib/
│   └── admin-auth.ts              # Auth utility functions
└── middleware.ts                  # Route protection

```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install jose
```

**Note**: `jose` is required for JWT handling.

### 2. Create Environment File

Create `frontend/.env.local` with:

```env
ADMIN_USERNAME=tsg_admin
ADMIN_PASSWORD=tsgtharsiyanshahastragautham321
ADMIN_JWT_SECRET=your-super-secret-jwt-key-change-in-production-12345678
ADMIN_SESSION_EXPIRY=24
```

⚠️ **IMPORTANT**: Change `ADMIN_JWT_SECRET` in production!

### 3. Start Development Server

```bash
npm run dev
```

### 4. Access Admin Dashboard

Navigate to: `http://localhost:3000/admin/login`

Login with:
- **Username**: `tsg_admin`
- **Password**: `tsgtharsiyanshahastragautham321`

## 📊 Dashboard Pages

### 1. Dashboard Overview (`/admin`)

- Total users count
- AI posts generated
- Active companies
- Recent activity feed
- Popular aspect ratios chart
- Most active companies chart

### 2. Users Management (`/admin/users`)

- User list with pagination
- Search by name, email, or company
- User status badges (active/inactive/suspended)
- Actions: View, Edit, Delete
- Export to CSV

### 3. Analytics (`/admin/analytics`)

- Revenue metrics
- Page views
- Conversion rates
- User growth charts
- Post generation trends
- Feature usage statistics
- Device breakdown
- Google Analytics integration placeholder

### 4. Settings (`/admin/settings`)

- Admin profile display
- Password change
- Dark/Light mode toggle
- Notification preferences
- Email alerts configuration

## 🎨 UI Components

### ShadCN Components Used

- `Button` - Primary actions
- `Card` - Content containers
- `Input` - Form inputs
- `Label` - Form labels
- `Badge` - Status indicators
- `Table` - Data tables
- `Switch` - Toggle switches
- `Separator` - Visual dividers
- `Tabs` - Tabbed interfaces
- `Avatar` - User avatars

### Custom Admin Components

#### `<Sidebar />`
Left navigation with:
- Dashboard link
- Users link
- Analytics link
- Settings link
- User info & logout

#### `<Navbar />`
Top bar with:
- Welcome message
- Notification bell
- Theme toggle

#### `<StatsCard />`
Metric display with:
- Title & icon
- Value
- Description
- Trend indicator

#### `<UserTable />`
User management with:
- Sortable columns
- Status badges
- Action buttons
- Pagination

#### `<AnalyticsChart />`
Data visualization:
- Bar chart display
- Custom data points
- Responsive design

## 🔒 Security Best Practices

### Current Implementation

✅ httpOnly cookies  
✅ JWT token validation  
✅ Session expiry (24h)  
✅ Middleware protection  
✅ Secure flag in production  
✅ Path-scoped cookies  

### Production Recommendations

1. **Change Default Credentials**
   ```env
   ADMIN_USERNAME=your_secure_username
   ADMIN_PASSWORD=your_very_strong_password_here
   ```

2. **Generate Secure JWT Secret**
   ```bash
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

3. **Enable HTTPS**
   - Set `HTTPS=true` in environment
   - Use SSL certificates
   - Enable `SECURE_SSL_REDIRECT`

4. **Rate Limiting**
   - Add rate limiting to login endpoint
   - Use packages like `express-rate-limit`

5. **Audit Logging**
   - Log all admin actions
   - Track failed login attempts
   - Monitor suspicious activity

6. **Two-Factor Authentication** (Future)
   - Add 2FA support
   - Use authenticator apps
   - Backup codes

## 🛠️ Customization

### Adding New Admin Pages

1. Create page at `frontend/src/app/admin/your-page/page.tsx`:

```tsx
'use client';

export default function YourAdminPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Your Page</h1>
      {/* Your content */}
    </div>
  );
}
```

2. Add link to `frontend/src/components/admin/Sidebar.tsx`:

```tsx
{
  title: 'Your Page',
  href: '/admin/your-page',
  icon: YourIcon,
}
```

### Changing Session Duration

Edit `frontend/.env.local`:

```env
ADMIN_SESSION_EXPIRY=48  # 48 hours
```

### Customizing Theme

The dashboard uses TailwindCSS. Modify colors in `frontend/tailwind.config.ts`:

```ts
theme: {
  extend: {
    colors: {
      primary: 'your-color',
      // ...
    }
  }
}
```

## 🔄 Integration with Backend

### Connecting to Real Data

Replace mock data in pages with API calls:

```tsx
// Example: Fetching users
const [users, setUsers] = useState<User[]>([]);

useEffect(() => {
  async function fetchUsers() {
    const response = await fetch('/api/users');
    const data = await response.json();
    setUsers(data);
  }
  fetchUsers();
}, []);
```

### Creating Admin API Routes

Add admin endpoints in `backend/` and call from frontend:

```tsx
// In your admin page
const response = await fetch('http://localhost:8000/api/admin/users', {
  headers: {
    'Authorization': `Bearer ${token}`,
  }
});
```

## 📱 Responsive Design

The dashboard is fully responsive:

- **Desktop**: Full sidebar + content
- **Tablet**: Collapsible sidebar
- **Mobile**: Bottom navigation (optional)

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

## 🧪 Testing

### Manual Testing Checklist

- [ ] Login with correct credentials
- [ ] Login with incorrect credentials shows error
- [ ] Session persists across page refreshes
- [ ] Logout clears session
- [ ] Protected routes redirect to login when not authenticated
- [ ] All dashboard pages load correctly
- [ ] Dark/Light mode toggle works
- [ ] Responsive design on mobile/tablet

### Future Automated Tests

Consider adding:
- Unit tests (Jest/Vitest)
- E2E tests (Playwright)
- Integration tests

## 🚨 Troubleshooting

### "Session Expired" Error

**Solution**: The JWT token expired. Login again.

### Can't Access Admin Routes

**Solution**: 
1. Check `.env.local` exists with credentials
2. Verify middleware.ts is configured
3. Clear browser cookies
4. Check console for errors

### "jose" Module Not Found

**Solution**: Install dependencies:
```bash
cd frontend && npm install jose
```

### Dark Mode Not Working

**Solution**: Check localStorage and document.documentElement:
```js
localStorage.getItem('theme')
document.documentElement.classList.contains('dark')
```

## 📈 Future Enhancements

### Planned Features

- [ ] Two-factor authentication
- [ ] Activity logs & audit trail
- [ ] Advanced analytics with charts (recharts integration)
- [ ] Real-time notifications
- [ ] User impersonation
- [ ] Bulk user operations
- [ ] Export reports (PDF/CSV)
- [ ] Google Analytics integration
- [ ] Role-based access control (multiple admin levels)
- [ ] API rate limiting dashboard

### Google Analytics Integration

Placeholder is ready at `/admin/analytics`. To integrate:

1. Install GA package:
```bash
npm install react-ga4
```

2. Add GA tracking ID to `.env.local`:
```env
NEXT_PUBLIC_GA_TRACKING_ID=G-XXXXXXXXXX
```

3. Initialize in layout:
```tsx
import ReactGA from 'react-ga4';

ReactGA.initialize(process.env.NEXT_PUBLIC_GA_TRACKING_ID);
```

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review error logs in browser console
3. Check middleware.ts configuration
4. Verify environment variables

## 🎉 Credits

Built with:
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **ShadCN UI** - Component library
- **jose** - JWT handling
- **Lucide React** - Icons

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-30  
**Maintainer**: TSG Team

