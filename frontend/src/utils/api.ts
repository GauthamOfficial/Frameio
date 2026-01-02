/**
 * Centralized API utility for making requests to the Django backend
 * 
 * URL Strategy:
 * - Client-side (browser): Uses relative paths like '/api/...' which are routed through Nginx
 * - Server-side (SSR): Uses absolute URLs from NEXT_PUBLIC_API_BASE_URL environment variable
 */

interface LimitError extends Error {
  limit_type?: string;
  current_count?: number;
  limit?: number;
  reset_date?: string;
  isLimitError?: boolean;
}

/**
 * Get the API base URL for the current execution context
 * 
 * - In browser (client-side): Returns empty string to use relative paths
 * - In server-side (SSR/build): Returns absolute URL from NEXT_PUBLIC_API_BASE_URL
 * 
 * @returns Base URL string (empty for client-side, absolute URL for server-side)
 */
function getApiBaseUrl(): string {
  // Client-side: use relative paths (routed through Nginx)
  if (typeof window !== 'undefined') {
    return '';
  }
  
  // Server-side: use absolute URL from environment variable
  // NEXT_PUBLIC_API_BASE_URL must be set for SSR to work correctly
  // Example: NEXT_PUBLIC_API_BASE_URL=http://13.213.53.199 (without /api suffix)
  // For development: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
  const serverBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (serverBaseUrl) {
    // Remove trailing slashes
    return serverBaseUrl.replace(/\/+$/, '');
  }
  
  // If NEXT_PUBLIC_API_BASE_URL is not set, return empty string
  // This will cause buildApiUrl to use relative paths, which won't work in SSR
  // but will work in client-side code. Developers should set NEXT_PUBLIC_API_BASE_URL
  // for proper SSR support.
  return '';
}

export const API_BASE_URL = getApiBaseUrl();

/**
 * Get base URL without /api suffix (for media/static files)
 * Only used in server-side contexts
 */
function getBaseUrlWithoutApi(): string {
  const apiUrl = getApiBaseUrl();
  // Remove /api suffix if present
  return apiUrl.replace(/\/api\/?$/, '');
}

/**
 * Build API URL for the current execution context
 * 
 * Client-side (browser):
 *   - Returns relative paths like '/api/users/auth/login/'
 *   - These are routed through Nginx to the backend
 * 
 * Server-side (SSR):
 *   - Returns absolute URLs like 'http://13.213.53.199/api/users/auth/login/'
 *   - Uses NEXT_PUBLIC_API_BASE_URL environment variable
 * 
 * @param endpoint - API endpoint path (e.g., '/api/users/' or '/users/')
 * @returns Full URL (relative for client, absolute for server)
 */
export function buildApiUrl(endpoint: string): string {
  // If endpoint is already absolute, return as-is
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }
  
  // Normalize endpoint to start with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Client-side: return relative path (will be routed through Nginx)
  if (typeof window !== 'undefined') {
    // Ensure endpoint starts with /api/
    if (normalizedEndpoint.startsWith('/api/')) {
      return normalizedEndpoint;
    }
    // If endpoint doesn't start with /api/, add it
    return `/api${normalizedEndpoint}`;
  }
  
  // Server-side: build absolute URL
  const baseUrl = API_BASE_URL;
  
  // If baseUrl is empty (shouldn't happen, but handle gracefully)
  if (!baseUrl) {
    // Fallback to relative path even in SSR (not ideal, but better than breaking)
    return normalizedEndpoint.startsWith('/api/') ? normalizedEndpoint : `/api${normalizedEndpoint}`;
  }
  
  // Server-side: construct absolute URL
  // Handle /api prefix correctly
  if (normalizedEndpoint.startsWith('/api/')) {
    // Endpoint already has /api/, append to base URL
    return `${baseUrl}${normalizedEndpoint}`;
  } else {
    // Endpoint doesn't have /api/, add it
    return `${baseUrl}/api${normalizedEndpoint}`;
  }
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
 * Build full URL from endpoint path (used by apiGet, apiPost, etc.)
 * Delegates to buildApiUrl for consistency
 */
function buildUrl(endpoint: string): string {
  return buildApiUrl(endpoint);
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
    
    // Create error with full error data for limit errors (403)
    if (response.status === 403 && errorData.error) {
      const error = new Error(errorData.error) as LimitError;
      // Attach additional error data to the error object for limit errors
      // Always attach these properties if they exist in errorData
      if (errorData.limit_type !== undefined) {
        error.limit_type = errorData.limit_type as string;
      }
      if (errorData.current_count !== undefined) {
        error.current_count = errorData.current_count as number;
      }
      if (errorData.limit !== undefined) {
        error.limit = errorData.limit as number;
      }
      if (errorData.reset_date !== undefined) {
        error.reset_date = errorData.reset_date as string;
      }
      // Mark this as a limit error so it can be handled specially
      error.isLimitError = true;
      throw error;
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
  
  // Get response text first (can only read once)
  const text = await response.text();
  
  // If text is empty, return null
  if (!text || text.trim() === '') {
    return null as T;
  }
  
  // Check if response looks like HTML (common error pages) - do this BEFORE trying to parse
  const trimmedText = text.trim();
  if (trimmedText.startsWith('<!DOCTYPE') || trimmedText.startsWith('<html') || trimmedText.startsWith('<!')) {
    const contentType = response.headers.get('content-type') || 'not set';
    throw new Error(`Backend returned HTML instead of JSON. This usually means the endpoint is incorrect or the server returned an error page. Content-Type: ${contentType}`);
  }
  
  // Try to parse as JSON
  try {
    return JSON.parse(text) as T;
  } catch (error) {
    // If it's a JSON parsing error, provide helpful message
    if (error instanceof SyntaxError) {
      // Check if the text that failed to parse looks like HTML
      if (trimmedText.includes('<!DOCTYPE') || trimmedText.includes('<html') || trimmedText.includes('<!')) {
        throw new Error(`Backend returned HTML error page instead of JSON. The endpoint may be incorrect or the server may be down.`);
      }
      // If it's an "Unexpected end of JSON input" error, the response was empty or incomplete
      if (error.message.includes('JSON') || error.message.includes('Unexpected token')) {
        // Provide helpful error message
        throw new Error(`Failed to parse JSON response: ${error.message}. Response preview: ${text.substring(0, 100)}`);
      }
      // Re-throw syntax errors that aren't JSON-related
      throw error;
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
 * 
 * Client-side: Returns relative paths (routed through Nginx)
 * Server-side: Returns absolute URLs using NEXT_PUBLIC_API_BASE_URL
 */
export function getFullUrl(path: string): string {
  if (!path) return '';
  
  // If already absolute URL, return as-is
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  
  // Client-side: return relative paths
  if (typeof window !== 'undefined') {
    // Ensure path starts with /
    return path.startsWith('/') ? path : `/${path}`;
  }
  
  // Server-side: build absolute URLs for media/static files
  const baseUrl = getBaseUrlWithoutApi();
  
  // Media files are served directly by nginx, not through API
  if (path.startsWith('/media/') || path.startsWith('/static/')) {
    if (baseUrl) {
      return `${baseUrl}${path}`;
    }
    // Fallback to relative if baseUrl not set
    return path;
  }
  
  // For other paths, use API base URL
  if (baseUrl) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${baseUrl}${normalizedPath}`;
  }
  
  // Fallback to relative path
  return path.startsWith('/') ? path : `/${path}`;
}

