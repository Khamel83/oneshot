/**
 * auth.js — shared auth helpers for all pages (multi-tenant aware).
 *
 * Automatically detects the site slug from the URL path.
 * All API calls are scoped to the current site.
 *
 * Storage (per site):
 *   app_token_{site}   — Supabase JWT
 *   app_member_{site}  — JSON of the member object
 *
 * Usage:
 *   import { getSite, getToken, getMember, isLoggedIn, api, signOut, requireAuth } from '/js/auth.js';
 */

/**
 * Detect the site slug from the current URL path.
 * /gambling/dashboard → "gambling"
 * /login → null (root level, no site context)
 * / → null
 */
export function getSite() {
    const parts = window.location.pathname.split('/').filter(Boolean);
    // If first segment is not a known page, it's a site slug
    const pages = ['login', 'dashboard', 'admin', 'api'];
    if (parts.length >= 1 && !pages.includes(parts[0])) {
        return parts[0];
    }
    return null;
}

/**
 * Get a site-scoped storage key.
 */
function storageKey(suffix) {
    const site = getSite();
    return site ? `app_${suffix}_${site}` : `app_${suffix}`;
}

export function getToken() {
    return localStorage.getItem(storageKey('token')) || '';
}

export function getMember() {
    try {
        return JSON.parse(localStorage.getItem(storageKey('member')) || '{}');
    } catch {
        return {};
    }
}

export function isLoggedIn() {
    return !!(getToken() && getMember().email);
}

export function isAdmin() {
    return getMember().is_admin === true;
}

export function saveSession(token, member) {
    localStorage.setItem(storageKey('token'), token);
    localStorage.setItem(storageKey('member'), JSON.stringify(member));
}

export function signOut() {
    const site = getSite();
    localStorage.removeItem(storageKey('token'));
    localStorage.removeItem(storageKey('member'));
    window.location.href = site ? `/${site}/login` : '/login';
}

export function requireAuth() {
    if (!isLoggedIn()) {
        const site = getSite();
        window.location.href = site ? `/${site}/login` : '/login';
        return false;
    }
    return true;
}

export function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
        const site = getSite();
        window.location.href = site ? `/${site}/dashboard` : '/dashboard';
        return false;
    }
    return true;
}

/**
 * Site-scoped API URL builder.
 * api('/auth', {action: 'login'}) → '/gambling/api/auth' if on gambling site
 */
export function api(path) {
    const site = getSite();
    if (site) {
        return `/${site}/api/${path}`;
    }
    return `/api/${path}`;
}

/**
 * Site-scoped page URL builder.
 * page('dashboard') → '/gambling/dashboard'
 */
export function page(path) {
    const site = getSite();
    if (site) {
        return `/${site}/${path}`;
    }
    return `/${path}`;
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
