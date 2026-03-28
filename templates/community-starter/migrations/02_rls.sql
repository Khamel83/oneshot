-- =============================================================================
-- Community Starter — Row Level Security
-- Run AFTER 01_schema.sql
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE members  ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_log ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- members policies
-- =============================================================================

-- Public can read name/avatar (no PII) — via the API's explicit column select
-- The API uses SERVICE_ROLE_KEY which bypasses RLS.
-- These policies protect against direct Supabase REST calls with the anon key.

-- Anon: deny all
CREATE POLICY "anon_deny_members_select" ON members
    FOR SELECT TO anon USING (false);
CREATE POLICY "anon_deny_members_insert" ON members
    FOR INSERT TO anon WITH CHECK (false);
CREATE POLICY "anon_deny_members_update" ON members
    FOR UPDATE TO anon USING (false);
CREATE POLICY "anon_deny_members_delete" ON members
    FOR DELETE TO anon USING (false);

-- Authenticated: can read all members (API layer enforces column filtering)
CREATE POLICY "auth_read_members" ON members
    FOR SELECT TO authenticated USING (true);

-- Authenticated: can only update their own row
CREATE POLICY "auth_update_own_member" ON members
    FOR UPDATE TO authenticated USING (auth.uid() = user_id);

-- Service role: full access (used by API — bypasses RLS automatically)

-- =============================================================================
-- email_log policies
-- =============================================================================

-- Nobody reads email_log via direct Supabase calls — only via service role in API
CREATE POLICY "anon_deny_email_log" ON email_log
    FOR ALL TO anon USING (false);
CREATE POLICY "auth_deny_email_log" ON email_log
    FOR ALL TO authenticated USING (false);

-- =============================================================================
-- Trigger: auto-deny-all RLS for any future tables
-- Protects against forgetting to set RLS on new tables.
-- =============================================================================
CREATE OR REPLACE FUNCTION public.auto_enable_rls()
RETURNS event_trigger
LANGUAGE plpgsql AS $$
DECLARE
    obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE %s ENABLE ROW LEVEL SECURITY', obj.object_identity);
        RAISE NOTICE 'Enabled RLS on %', obj.object_identity;
    END LOOP;
END;
$$;

DROP EVENT TRIGGER IF EXISTS auto_rls_on_create;
CREATE EVENT TRIGGER auto_rls_on_create
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE')
    EXECUTE FUNCTION public.auto_enable_rls();
