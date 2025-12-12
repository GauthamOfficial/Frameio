/**
 * Centralized API utility for making requests to the Django backend
 * Automatically switches between localhost (development) and production URL
 */

// Determine API base URL based on environment
export const API_BASE_URL = 
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'
    : (process.env.NEXT_PUBLIC_API_URL || 'http://13.213.53.199/api');

/**
 * Helper function to build full API URLs, handling /api prefix correctly
 * @param endpoint - API endpoint path (e.g., '/api/users/' or '/users/')
 * @returns Full URL with proper /api handling
 */
export function buildApiUrl(endpoint: string): string {
  // If endpoint is already absolute, return as-is
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }
  
  const baseUrl = API_BASE_URL.replace(/\/+$/, '');
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // If baseUrl already ends with /api and endpoint starts with /api/, remove /api from endpoint
  if (baseUrl.endsWith('/api') && normalizedEndpoint.startsWith('/api/')) {
    return `${baseUrl}${normalizedEndpoint.replace(/^\/api/, '')}`;
  }
  
  // If baseUrl doesn't end with /api but endpoint starts with /api/, use as-is
  // If baseUrl ends with /api but endpoint doesn't start with /api/, use as-is
  return `${baseUrl}${normalizedEndpoint}`;
}

/**
 * Get authentication token from various sources
 * @param providedToken - Optional token to use (e.g., JWT token)
 */
async function getAuthToken(providedToken?: string | null): Promise<string | null> {
  // Use provided token if available
  if (providedToken) {
    return providedToken;
  }
  
  // Check localStorage for stored token
  if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      return storedToken;
    }
  }
  
  return null;
}

/**
 * Get development headers (X-Dev-User-ID, X-Dev-Org-ID) if available
 */
function getDevHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  
  if (typeof window !== 'undefined') {
    const devUserId = localStorage.getItem('dev-user-id');
    const devOrgId = localStorage.getItem('dev-org-id');
    
    if (devUserId && devOrgId) {
      headers['X-Dev-User-ID'] = devUserId;
      headers['X-Dev-Org-ID'] = devOrgId;
    }
  }
  
  return headers;
}

/**
 * Build full URL from endpoint path
 */
function buildUrl(endpoint: string): string {
  // If endpoint is already absolute, return as-is
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }
  
  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Handle /api prefix in base URL
  const baseUrl = API_BASE_URL.endsWith('/api') 
    ? API_BASE_URL 
    : API_BASE_URL;
  
  // Avoid double /api when baseUrl already contains /api
  if (baseUrl.endsWith('/api') && normalizedEndpoint.startsWith('/api/')) {
    return `${baseUrl}${normalizedEndpoint.replace(/^\/api/, '')}`;
  }
  
  return `${baseUrl}${normalizedEndpoint}`;
}

/**
 * Build request headers with authentication and dev headers
 * @param providedToken - Optional token to use (e.g., JWT token)
 */
async function buildHeaders(customHeaders: Record<string, string> = {}, providedToken?: string | null): Promise<Record<string, string>> {
  const token = await getAuthToken(providedToken);
  const devHeaders = getDevHeaders();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...devHeaders,
    ...customHeaders,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * Handle fetch response and parse JSON
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    let errorData;
    try {
      errorData = JSON.parse(errorText);
    } catch {
      errorData = { error: errorText };
    }
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }
  
  // Handle empty responses (204 No Content)
  if (response.status === 204) {
    return null as T;
  }
  
  // Check content-length header for empty responses
  const contentLength = response.headers.get('content-length');
  if (contentLength === '0') {
    return null as T;
  }
  
  // Try to parse JSON, handle empty responses gracefully
  try {
    const text = await response.text();
    
    // If text is empty, return null
    if (!text || text.trim() === '') {
      return null as T;
    }
    
    // Try to parse as JSON
    return JSON.parse(text) as T;
  } catch (error) {
    // If it's an "Unexpected end of JSON input" error, the response was empty
    if (error instanceof SyntaxError && error.message.includes('JSON')) {
      return null as T;
    }
    // Re-throw other errors
    throw error;
  }
}

/**
 * GET request helper
 * @param path - API endpoint path (e.g., '/api/users/')
 * @param options - Fetch options
 * @param token - Optional authentication token (e.g., JWT token)
 */
export async function apiGet<T = unknown>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = buildUrl(path);
  const headers = await buildHeaders(options.headers as Record<string, string>, token);
  
  const response = await fetch(url, {
    ...options,
    method: 'GET',
    headers: headers as HeadersInit,
  });
  
  return handleResponse<T>(response);
}

/**
 * POST request helper
 * @param path - API endpoint path (e.g., '/api/users/')
 * @param body - Request body (will be JSON stringified unless FormData)
 * @param options - Fetch options
 * @param token - Optional authentication token (e.g., JWT token)
 */
export async function apiPost<T = unknown>(
  path: string,
  body?: unknown,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = buildUrl(path);
  
  // Check if body is FormData
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  
  // Build headers (don't set Content-Type for FormData)
  const customHeaders: Record<string, string> = {};
  if (!isFormData) {
    customHeaders['Content-Type'] = 'application/json';
  }
  
  const headers = await buildHeaders({
    ...customHeaders,
    ...(options.headers as Record<string, string> || {}),
  }, token);
  
  // Remove Content-Type from headers if FormData (browser will set it with boundary)
  if (isFormData) {
    delete headers['Content-Type'];
  }
  
  const response = await fetch(url, {
    ...options,
    method: 'POST',
    headers: headers as HeadersInit,
    body: isFormData ? body as FormData : body !== undefined ? JSON.stringify(body) : undefined,
  });
  
  return handleResponse<T>(response);
}

/**
 * PUT request helper
 * @param path - API endpoint path
 * @param body - Request body
 * @param options - Fetch options
 * @param token - Optional authentication token
 */
export async function apiPut<T = unknown>(
  path: string,
  body?: unknown,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = buildUrl(path);
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  
  const customHeaders: Record<string, string> = {};
  if (!isFormData) {
    customHeaders['Content-Type'] = 'application/json';
  }
  
  const headers = await buildHeaders({
    ...customHeaders,
    ...(options.headers as Record<string, string> || {}),
  }, token);
  
  if (isFormData) {
    delete headers['Content-Type'];
  }
  
  const response = await fetch(url, {
    ...options,
    method: 'PUT',
    headers: headers as HeadersInit,
    body: isFormData ? body as FormData : body !== undefined ? JSON.stringify(body) : undefined,
  });
  
  return handleResponse<T>(response);
}

/**
 * PATCH request helper
 * @param path - API endpoint path
 * @param body - Request body
 * @param options - Fetch options
 * @param token - Optional authentication token
 */
export async function apiPatch<T = unknown>(
  path: string,
  body?: unknown,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = buildUrl(path);
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  
  const customHeaders: Record<string, string> = {};
  if (!isFormData) {
    customHeaders['Content-Type'] = 'application/json';
  }
  
  const headers = await buildHeaders({
    ...customHeaders,
    ...(options.headers as Record<string, string> || {}),
  }, token);
  
  if (isFormData) {
    delete headers['Content-Type'];
  }
  
  const response = await fetch(url, {
    ...options,
    method: 'PATCH',
    headers: headers as HeadersInit,
    body: isFormData ? body as FormData : body !== undefined ? JSON.stringify(body) : undefined,
  });
  
  return handleResponse<T>(response);
}

/**
 * DELETE request helper
 * @param path - API endpoint path
 * @param options - Fetch options
 * @param token - Optional authentication token
 */
export async function apiDelete<T = unknown>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const url = buildUrl(path);
  const headers = await buildHeaders(options.headers as Record<string, string>, token);
  
  const response = await fetch(url, {
    ...options,
    method: 'DELETE',
    headers: headers as HeadersInit,
  });
  
  return handleResponse<T>(response);
}

/**
 * Helper to get full URL for an image or asset
 * Useful when backend returns relative paths
 */
export function getFullUrl(path: string): string {
  if (!path) return '';
  
  // If already absolute URL, return as-is
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  
  // Media files are served directly by nginx, not through API
  if (path.startsWith('/media/')) {
    const baseUrl = process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000'
      : (process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://13.213.53.199');
    return `${baseUrl}${path}`;
  }
  
  // Static files are also served directly
  if (path.startsWith('/static/')) {
    const baseUrl = process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000'
      : (process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://13.213.53.199');
    return `${baseUrl}${path}`;
  }
  
  // If path starts with /, it's relative to API base
  if (path.startsWith('/')) {
    return `${API_BASE_URL}${path}`;
  }
  
  // Otherwise, assume it's relative to API base
  return `${API_BASE_URL}/${path}`;
}

