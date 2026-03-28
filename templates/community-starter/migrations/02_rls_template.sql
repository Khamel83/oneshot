-- =============================================================================
-- Per-Site RLS Template
-- Run this for EACH new site, replacing {{SLUG}} with the site slug.
-- =============================================================================

-- !!! Replace {{SLUG}} with your site slug before running !!!

-- Enable RLS on all tables in this site's schema
ALTER TABLE {{SLUG}}.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE {{SLUG}}.email_log ENABLE ROW LEVEL SECURITY;

-- members: deny all anon access
CREATE POLICY "{{SLUG}}_anon_deny_members_select" ON {{SLUG}}.members
    FOR SELECT TO anon USING (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_insert" ON {{SLUG}}.members
    FOR INSERT TO anon WITH CHECK (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_update" ON {{SLUG}}.members
    FOR UPDATE TO anon USING (false);
CREATE POLICY "{{SLUG}}_anon_deny_members_delete" ON {{SLUG}}.members
    FOR DELETE TO anon USING (false);

-- members: authenticated users can read all members (API enforces column filtering)
CREATE POLICY "{{SLUG}}_auth_read_members" ON {{SLUG}}.members
    FOR SELECT TO authenticated USING (true);

-- members: authenticated users can only update their own row
CREATE POLICY "{{SLUG}}_auth_update_own_member" ON {{SLUG}}.members
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

-- email_log: deny all direct access (only service role in API)
CREATE POLICY "{{SLUG}}_anon_deny_email_log" ON {{SLUG}}.email_log
    FOR ALL TO anon USING (false);
CREATE POLICY "{{SLUG}}_auth_deny_email_log" ON {{SLUG}}.email_log
    FOR ALL TO authenticated USING (false);
