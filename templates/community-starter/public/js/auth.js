/**
 * auth.js — shared auth helpers for all pages.
 *
 * Storage:
 *   app_token  — Supabase JWT (from login response)
 *   app_member — JSON of the member object
 *
 * Usage:
 *   import { getToken, getMember, isLoggedIn, signOut, requireAuth, requireAdmin } from '/js/auth.js';
 */

const TOKEN_KEY  = 'app_token';
const MEMBER_KEY = 'app_member';

export function getToken() {
    return localStorage.getItem(TOKEN_KEY) || '';
}

export function getMember() {
    try {
        return JSON.parse(localStorage.getItem(MEMBER_KEY) || '{}');
    } catch {
        return {};
    }
}

export function isLoggedIn() {
    const token = getToken();
    const member = getMember();
    return !!(token && member.email);
}

export function isAdmin() {
    return getMember().is_admin === true;
}

export function saveSession(token, member) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(MEMBER_KEY, JSON.stringify(member));
}

export function signOut() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(MEMBER_KEY);
    window.location.href = '/login';
}

/**
 * Redirect to /login if not authenticated.
 * Call at the top of any protected page.
 */
export function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

/**
 * Redirect to /dashboard if not admin.
 */
export function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
        window.location.href = '/dashboard';
        return false;
    }
    return true;
}

/**
 * Convenience: fetch wrapper that adds Authorization header.
 */
export async function authFetch(url, options = {}) {
    const token = getToken();
    return fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
    });
}

/**
 * Handle 401 globally — session expired, force re-login.
 */
export function handleUnauthorized(response) {
    if (response.status === 401) {
        signOut();
        return true;
    }
    return false;
}
