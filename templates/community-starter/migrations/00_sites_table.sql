-- =============================================================================
-- Multi-Tenant: Sites Registry Table
-- Run this ONCE in Supabase Dashboard → SQL Editor (public schema)
-- =============================================================================

-- Table that tracks all sites/communities on this platform
CREATE TABLE IF NOT EXISTS public.sites (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    slug        text UNIQUE NOT NULL,          -- URL slug: khamel.com/{slug}
    name        text NOT NULL,                -- Display name: "Mrs. Smith's 2nd Grade"
    config      jsonb DEFAULT '{}'::jsonb,    -- Site-specific config (future use)
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Index for fast slug lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_sites_slug ON public.sites(slug);
