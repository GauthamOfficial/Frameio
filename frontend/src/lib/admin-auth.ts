import { cookies } from 'next/headers';
import { SignJWT, jwtVerify } from 'jose';

const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'tsg_admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'tsgtharsiyanshahastragautham321';
const JWT_SECRET = new TextEncoder().encode(
  process.env.ADMIN_JWT_SECRET || 'your-super-secret-jwt-key-change-in-production-12345678'
);
const SESSION_EXPIRY = parseInt(process.env.ADMIN_SESSION_EXPIRY || '24', 10);

export interface AdminSession {
  username: string;
  loginTime: number;
  expiresAt: number;
}

/**
 * Verify admin credentials
 */
export function verifyAdminCredentials(username: string, password: string): boolean {
  return username === ADMIN_USERNAME && password === ADMIN_PASSWORD;
}

/**
 * Create admin session token
 */
export async function createAdminSession(username: string): Promise<string> {
  const expiresAt = Date.now() + SESSION_EXPIRY * 60 * 60 * 1000; // Convert hours to milliseconds
  
  const token = await new SignJWT({ 
    username, 
    loginTime: Date.now(),
    expiresAt 
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime(`${SESSION_EXPIRY}h`)
    .sign(JWT_SECRET);

  return token;
}

/**
 * Verify admin session token
 */
export async function verifyAdminSession(token: string): Promise<AdminSession | null> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    
    const session = payload as unknown as AdminSession;
    
    // Check if session has expired
    if (session.expiresAt && Date.now() > session.expiresAt) {
      return null;
    }
    
    return session;
  } catch (error) {
    console.error('Admin session verification failed:', error);
    return null;
  }
}

/**
 * Set admin session cookie
 */
export async function setAdminSessionCookie(token: string) {
  const cookieStore = await cookies();
  
  // Only use Secure flag if we're actually using HTTPS
  // Set NEXT_PUBLIC_USE_HTTPS=true in environment when using HTTPS/SSL
  // Defaults to false for HTTP connections
  const isSecure = process.env.NEXT_PUBLIC_USE_HTTPS === 'true';
  
  cookieStore.set('admin-session', token, {
    httpOnly: true,
    secure: isSecure,  // Only secure if using HTTPS
    sameSite: 'lax',
    maxAge: SESSION_EXPIRY * 60 * 60, // Convert hours to seconds
    path: '/',
  });
}

/**
 * Get admin session from cookie
 */
export async function getAdminSession(): Promise<AdminSession | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('admin-session');
  
  if (!token) {
    return null;
  }
  
  return verifyAdminSession(token.value);
}

/**
 * Clear admin session cookie
 */
export async function clearAdminSession() {
  const cookieStore = await cookies();
  cookieStore.delete('admin-session');
}

/**
 * Check if user is authenticated as admin
 */
export async function isAdminAuthenticated(): Promise<boolean> {
  const session = await getAdminSession();
  return session !== null;
}

