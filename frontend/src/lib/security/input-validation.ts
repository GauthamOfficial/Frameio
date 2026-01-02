/**
 * Input validation utilities for API routes
 * Prevents injection attacks and validates user input
 */

/**
 * Validates and sanitizes a redirect path to prevent open redirect attacks
 */
export function validateRedirectPath(redirectPath: string | null, defaultPath: string = '/dashboard'): string {
  if (!redirectPath) {
    return defaultPath;
  }

  const trimmed = redirectPath.trim();
  
  // Must start with / to be a relative path
  if (!trimmed.startsWith('/')) {
    return defaultPath;
  }
  
  // Prevent path traversal attacks
  if (trimmed.includes('..') || trimmed.includes('//') || trimmed.includes('\\')) {
    return defaultPath;
  }
  
  // Prevent protocol-relative URLs
  if (trimmed.startsWith('//')) {
    return defaultPath;
  }
  
  // Prevent dangerous URL schemes
  const lowerTrimmed = trimmed.toLowerCase();
  if (lowerTrimmed.startsWith('javascript:') || 
      lowerTrimmed.startsWith('data:') ||
      lowerTrimmed.startsWith('vbscript:') ||
      lowerTrimmed.startsWith('file:')) {
    return defaultPath;
  }
  
  // Allow only safe characters
  if (!/^\/[a-zA-Z0-9\/\-_?=&]*$/.test(trimmed)) {
    return defaultPath;
  }
  
  // Limit path length
  if (trimmed.length > 500) {
    return defaultPath;
  }
  
  return trimmed;
}

/**
 * Validates JWT token format
 */
export function validateJWTToken(token: string | null): boolean {
  if (!token) {
    return false;
  }
  
  // JWT tokens have 3 parts separated by dots
  const jwtPattern = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_.]*$/;
  return jwtPattern.test(token);
}

/**
 * Sanitizes string input to prevent injection attacks
 */
export function sanitizeString(input: string | null | undefined, maxLength: number = 1000): string {
  if (!input) {
    return '';
  }
  
  // Remove null bytes
  let sanitized = input.replace(/\0/g, '');
  
  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  
  return sanitized.trim();
}

/**
 * Validates email format
 */
export function validateEmail(email: string | null): boolean {
  if (!email) {
    return false;
  }
  
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email) && email.length <= 254;
}

/**
 * Validates UUID format
 */
export function validateUUID(uuid: string | null): boolean {
  if (!uuid) {
    return false;
  }
  
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidPattern.test(uuid);
}

/**
 * Validates numeric ID (positive integer)
 */
export function validateNumericId(id: string | number | null): boolean {
  if (id === null || id === undefined) {
    return false;
  }
  
  const numId = typeof id === 'string' ? parseInt(id, 10) : id;
  return Number.isInteger(numId) && numId > 0;
}

/**
 * Validates that a URL stays on the same origin
 */
export function validateSameOrigin(url: string, baseUrl: string): boolean {
  try {
    const urlObj = new URL(url, baseUrl);
    const baseUrlObj = new URL(baseUrl);
    return urlObj.origin === baseUrlObj.origin;
  } catch {
    return false;
  }
}

/**
 * Sanitizes filename to prevent path traversal
 */
export function sanitizeFilename(filename: string): string {
  // Remove path components
  let sanitized = filename.replace(/[\/\\]/g, '');
  
  // Remove dangerous characters
  sanitized = sanitized.replace(/[<>:"|?*\x00-\x1f]/g, '');
  
  // Limit length
  if (sanitized.length > 255) {
    const ext = sanitized.substring(sanitized.lastIndexOf('.'));
    sanitized = sanitized.substring(0, 255 - ext.length) + ext;
  }
  
  return sanitized || 'file';
}

/**
 * Validates and sanitizes search query
 */
export function sanitizeSearchQuery(query: string | null, maxLength: number = 100): string {
  if (!query) {
    return '';
  }
  
  // Remove SQL injection patterns
  let sanitized = query.replace(/['";\\]/g, '');
  
  // Remove script tags
  sanitized = sanitized.replace(/<script[^>]*>.*?<\/script>/gi, '');
  
  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  
  return sanitized.trim();
}

