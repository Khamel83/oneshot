/**
 * config.js — Loads site theme config and applies CSS variables.
 * Call loadConfig() early in each page's <script>.
 */
import { getSite, api } from '/js/auth.js';

const THEME_PRESETS = {
    slate:  { accent_1: '#4f6df5', accent_2: '#7c5cbf', accent_3: '#89b4d4' },
    forest: { accent_1: '#16a34a', accent_2: '#15803d', accent_3: '#86efac' },
    sunset: { accent_1: '#ea580c', accent_2: '#dc2626', accent_3: '#fdba74' },
    mono:   { accent_1: '#6b7280', accent_2: '#374151', accent_3: '#d1d5db' },
};

let _config = null;

export async function loadConfig() {
    const site = getSite();
    if (!site) return;

    try {
        const res = await fetch(api('system?action=config'));
        if (!res.ok) return;
        const data = await res.json();
        if (!data.success) return;

        _config = { name: data.name, slug: data.slug, ...data.config };
        applyTheme(_config);
    } catch (e) {
        // Silent fail — use CSS defaults
    }
}

export function getConfig() {
    return _config;
}

export function getSiteName() {
    return _config?.name || '';
}

function applyTheme(config) {
    const root = document.documentElement;
    const preset = THEME_PRESETS[config.theme];
    const colors = preset || config;

    if (colors.accent_1) root.style.setProperty('--accent-1', colors.accent_1);
    if (colors.accent_2) root.style.setProperty('--accent-2', colors.accent_2);
    if (colors.accent_3) root.style.setProperty('--accent-3', colors.accent_3);

    if (config.font_display) {
        root.style.setProperty('--font-display', `'${config.font_display}', sans-serif`);
    }
    if (config.font_body) {
        root.style.setProperty('--font-body', `'${config.font_body}', sans-serif`);
    }

    // Rebuild gradient from accent colors
    const a1 = getComputedStyle(root).getPropertyValue('--accent-1').trim();
    const a2 = getComputedStyle(root).getPropertyValue('--accent-2').trim();
    const a3 = getComputedStyle(root).getPropertyValue('--accent-3').trim();
    root.style.setProperty('--bg-gradient', `linear-gradient(135deg, ${a1} 0%, ${a2} 50%, ${a3} 100%)`);
    document.body.style.background = `linear-gradient(135deg, ${a1} 0%, ${a2} 50%, ${a3} 100%)`;

    // Update page title
    if (config.name) {
        const base = document.title.split('—').pop()?.trim() || '';
        document.title = `${config.name} — ${base}`;
    }

    // Update logo text if element exists
    const logoEl = document.querySelector('.site-logo');
    if (logoEl && config.logo_text) {
        logoEl.textContent = config.logo_text;
    }
}
