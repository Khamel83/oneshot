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

-- Auto-create member row when a new user signs up
CREATE OR REPLACE FUNCTION {{SLUG}}.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = {{SLUG}}
AS $$
BEGIN
    INSERT INTO {{SLUG}}.members (user_id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    )
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

-- Wire trigger — only fires if user's app_metadata matches this site
-- This prevents cross-site member creation
DROP TRIGGER IF EXISTS {{SLUG}}_on_auth_user_created ON auth.users;
CREATE TRIGGER {{SLUG}}_on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    WHEN (NEW.raw_user_meta_data->>'site' = '{{SLUG}}')
    EXECUTE FUNCTION {{SLUG}}.handle_new_user();
