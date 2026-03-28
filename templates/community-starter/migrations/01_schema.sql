-- =============================================================================
-- Community Starter — Schema
-- Run this in Supabase Dashboard → SQL Editor
-- =============================================================================

-- Members table
-- user_id links to auth.users (Supabase Auth manages the auth side)
CREATE TABLE IF NOT EXISTS members (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     uuid UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email       text NOT NULL,
    name        text NOT NULL,
    bio         text,
    avatar_url  text,
    is_admin    boolean NOT NULL DEFAULT false,
    joined_at   timestamptz NOT NULL DEFAULT now()
);

-- Email audit log (for idempotency checks + debugging)
CREATE TABLE IF NOT EXISTS email_log (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    action          text NOT NULL,
    to_emails       text[] NOT NULL,
    period_label    text,
    resend_email_id text,
    sent_at         timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_members_user_id ON members(user_id);
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
CREATE INDEX IF NOT EXISTS idx_email_log_action_sent ON email_log(action, sent_at);

-- =============================================================================
-- Function: auto-create member row on signup
-- Triggered by Supabase Auth new user creation
-- =============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.members (user_id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    )
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

-- Wire trigger to auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
