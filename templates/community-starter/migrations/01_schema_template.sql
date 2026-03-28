-- =============================================================================
-- Per-Site Schema Template
-- Run this for EACH new site, replacing {{SLUG}} with the site slug.
-- Or use scripts/new-site.sh which does this automatically.
-- =============================================================================

-- !!! Replace {{SLUG}} with your site slug before running !!!

CREATE SCHEMA IF NOT EXISTS {{SLUG}};

-- Members table for this site
CREATE TABLE IF NOT EXISTS {{SLUG}}.members (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     uuid UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email       text NOT NULL,
    name        text NOT NULL,
    bio         text,
    avatar_url  text,
    is_admin    boolean NOT NULL DEFAULT false,
    joined_at   timestamptz NOT NULL DEFAULT now()
);

-- Email audit log for this site
CREATE TABLE IF NOT EXISTS {{SLUG}}.email_log (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    action          text NOT NULL,
    to_emails       text[] NOT NULL,
    period_label    text,
    resend_email_id text,
    sent_at         timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS {{SLUG}}_idx_members_user_id ON {{SLUG}}.members(user_id);
CREATE INDEX IF NOT EXISTS {{SLUG}}_idx_members_email ON {{SLUG}}.members(email);
CREATE INDEX IF NOT EXISTS {{SLUG}}_idx_email_log_action_sent ON {{SLUG}}.email_log(action, sent_at);

-- Member creation is handled by the API signup handler (api/handlers/auth.py)
-- which inserts directly into {site}.members using Accept-Profile header.
-- No trigger needed — the router knows the site from the URL path.

ALTER TABLE {{SLUG}}.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE {{SLUG}}.email_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "{{SLUG}}_anon_deny_members_select" ON {{SLUG}}.members FOR SELECT TO anon USING (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_insert" ON {{SLUG}}.members FOR INSERT TO anon WITH CHECK (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_update" ON {{SLUG}}.members FOR UPDATE TO anon USING (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_delete" ON {{SLUG}}.members FOR DELETE TO anon USING (false);
CREATE POLICY "{{SLUG}}_auth_read_members" ON {{SLUG}}.members FOR SELECT TO authenticated USING (true);
CREATE POLICY "{{SLUG}}_auth_update_own_member" ON {{SLUG}}.members FOR UPDATE TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "{{SLUG}}_anon_deny_email_log" ON {{SLUG}}.email_log FOR ALL TO anon USING (false);
CREATE POLICY "{{SLUG}}_auth_deny_email_log" ON {{SLUG}}.email_log FOR ALL TO authenticated USING (false);
