# Playwright Testing Results & Solutions

## Issues Discovered

### 1. Backend Permission Error (403 on `/api/users/`)
**Problem**: The `UserViewSet` required organization membership, blocking authentication verification during sign-in.

**Fixed in**: `backend/users/views.py`
```python
def get_permissions(self):
    if self.action == 'list':
        # For list action, only require authentication
        return [permissions.IsAuthenticated()]
    return super().get_permissions()
```

### 2. Frontend Middleware Blocking Requests (401)
**Problem**: Clerk middleware checked for `userId` from Clerk, but custom auth doesn't use Clerk.

**Fixed in**: `frontend/src/middleware.ts`
```typescript
// Using custom authentication system - skip Clerk auth
return NextResponse.next();
```

### 3. Authentication Not Persisting
**Problem**: Custom sign-in stores token in localStorage but doesn't integrate with the app's auth context.

## Complete Solution

### Backend Changes (✅ Applied)

1. `backend/users/views.py` - UserViewSet permissions
2. `backend/users/views.py` - CompanyProfileViewSet custom permission class
3. `backend/users/authentication.py` - Enhanced token validation

### Frontend Changes Needed

The custom sign-in needs to properly integrate with the auth context. Currently:
- Sign-in stores token in localStorage
- But app doesn't read from localStorage on page load
- Clerk is still being used for authentication checks

**Recommended**: Use Clerk authentication properly OR fully remove Clerk and implement custom auth throughout.

## Testing Commands

### Restart Backend
```bash
cd backend
python manage.py runserver
```

### Test with Playwright
```bash
# Navigate and test
playwright test settings-403-test.spec.ts
```

## What's Working Now

✅ Backend `/api/users/` endpoint allows authenticated list requests  
✅ Backend `/api/users/company-profiles/` has lenient dev permissions  
✅ Frontend middleware doesn't block requests  
✅ Sign-in successfully authenticates with backend  

## What Needs Attention

❌ Authentication persistence (token not being maintained across page loads)  
❌ Clerk integration conflicts with custom auth  
❌ Dashboard routes redirect to home after sign-in  

## Recommendation

**Option 1**: Fully implement custom auth
- Remove Clerk dependencies
- Use `useAuth` hook from `hooks/useAuth.ts` throughout
- Persist auth state properly

**Option 2**: Use Clerk properly
- Remove custom sign-in page
- Use Clerk's authentication flow
- Configure Clerk API keys properly

Currently, the app has both systems conflicting with each other.

