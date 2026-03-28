#!/usr/bin/env bash
# new-site.sh — Create a new private site in the multi-tenant platform
#
# Usage:
#   ./scripts/new-site.sh <slug> "<name>" --admin-email <email> [--theme <preset>]
#
# Example:
#   ./scripts/new-site.sh kids-class "Mrs. Smith's 2nd Grade" --admin-email me@khamel.com
#   ./scripts/new-site.sh poker "Friday Poker" --admin-email me@khamel.com --theme sunset
#   ./scripts/new-site.sh poker "Friday Poker" --admin-email me@khamel.com --accent "#ea580c,#dc2626,#fdba74" --logo "poker"
#
# Theme presets: slate (default), forest, sunset, mono
# Or use --accent "color1,color2,color3" for custom gradient
#
# Required env vars:
#   SUPABASE_URL           — e.g. https://abcdef.supabase.co
#   SUPABASE_SERVICE_ROLE_KEY — server-side key (bypasses RLS)

set -uo pipefail

# --- Theme presets ---
THEMES=(
    "slate|#4f6df5|#7c5cbf|#89b4d4"
    "forest|#16a34a|#15803d|#86efac"
    "sunset|#ea580c|#dc2626|#fdba74"
    "mono|#6b7280|#374151|#d1d5db"
)

# --- Args ---
SLUG="$1"
NAME="$2"
ADMIN_EMAIL=""
THEME="slate"
ACCENT_CUSTOM=""
LOGO_TEXT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --admin-email) ADMIN_EMAIL="$2"; shift 2 ;;
        --admin-password) ADMIN_PASSWORD="$2"; shift 2 ;;
        --theme) THEME="$2"; shift 2 ;;
        --accent) ACCENT_CUSTOM="$2"; shift 2 ;;
        --logo) LOGO_TEXT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# --- Resolve theme colors ---
resolve_theme() {
    local theme="$1"
    for entry in "${THEMES[@]}"; do
        IFS='|' read -r name c1 c2 c3 <<< "$entry"
        if [ "$name" = "$theme" ]; then
            echo "$c1|$c2|$c3"
            return
        fi
    done
    echo "Unknown theme '$theme'. Choose: slate, forest, sunset, mono"
    exit 1
}

if [ -n "$ACCENT_CUSTOM" ]; then
    IFS=',' read -r ACCENT_1 ACCENT_2 ACCENT_3 <<< "$ACCENT_CUSTOM"
else
    IFS='|' read -r ACCENT_1 ACCENT_2 ACCENT_3 <<< "$(resolve_theme "$THEME")"
fi

if [ -z "$LOGO_TEXT" ]; then
    LOGO_TEXT="$NAME"
fi

# --- Validate ---
if [ -z "$SLUG" ]; then
    echo "Usage: new-site.sh <slug> \"<name>\" --admin-email <email> [--theme <preset>] [--accent \"c1,c2,c3\"] [--logo <text>]"
    exit 1
fi

if [ -z "$NAME" ]; then
    NAME="$SLUG"
fi

# Validate slug: lowercase, alphanumeric + hyphens, 3-30 chars
if ! echo "$SLUG" | grep -qE '^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$'; then
    echo "ERROR: Invalid slug '$SLUG'. Must be 3-30 chars, lowercase alphanumeric + hyphens."
    exit 1
fi

if [ -z "$ADMIN_EMAIL" ]; then
    echo "ERROR: --admin-email is required"
    exit 1
fi

# --- Env vars ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

SUPABASE_URL="${SUPABASE_URL:?SUPABASE_URL not set}"
SERVICE_KEY="${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY not set}"
SITE_URL="${SITE_URL:-https://khamel.com}"

echo "=== Creating site: $SLUG ==="
echo "    Name: $NAME"
echo "    Admin: $ADMIN_EMAIL"
echo "    Theme: $THEME"
echo "    Colors: $ACCENT_1, $ACCENT_2, $ACCENT_3"
echo ""

# --- Check if site already exists ---
echo "Checking if site exists..."
EXISTS=$(curl -s "$SUPABASE_URL/rest/v1/sites?select=id&slug=eq.$SLUG" \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('yes' if data else 'no')
" 2>/dev/null)

if [ "$EXISTS" = "yes" ]; then
    echo "ERROR: Site '$SLUG' already exists."
    exit 1
fi
echo "    Site available."

# --- Generate admin password if not provided ---
if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d '=/+' | head -c 16)
fi

# --- Create schema ---
echo "Creating schema..."
SCHEMA_SQL="
CREATE SCHEMA IF NOT EXISTS $SLUG;

CREATE TABLE IF NOT EXISTS $SLUG.members (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     uuid UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email       text NOT NULL,
    name        text NOT NULL,
    bio         text,
    avatar_url  text,
    is_admin    boolean NOT NULL DEFAULT false,
    joined_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS $SLUG.email_log (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    action          text NOT NULL,
    to_emails       text[] NOT NULL,
    period_label    text,
    resend_email_id text,
    sent_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ${SLUG}_idx_members_user_id ON $SLUG.members(user_id);
CREATE INDEX IF NOT EXISTS ${SLUG}_idx_members_email ON $SLUG.members(email);
CREATE INDEX IF NOT EXISTS ${SLUG}_idx_email_log_action_sent ON $SLUG.email_log(action, sent_at);

# Member creation handled by API signup handler (api/handlers/auth.py)
# No trigger needed — router extracts site from URL path, handler inserts directly.

ALTER TABLE $SLUG.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE $SLUG.email_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY \"${SLUG}_anon_deny_members_select\" ON $SLUG.members FOR SELECT TO anon USING (false);
CREATE POLICY \"${SLUG}_anon_deny_members_insert\" ON $SLUG.members FOR INSERT TO anon WITH CHECK (false);
CREATE POLICY \"${SLUG}_anon_deny_members_update\" ON $SLUG.members FOR UPDATE TO anon USING (false);
CREATE POLICY \"${SLUG}_anon_deny_members_delete\" ON $SLUG.members FOR DELETE TO anon USING (false);
CREATE POLICY \"${SLUG}_auth_read_members\" ON $SLUG.members FOR SELECT TO authenticated USING (true);
CREATE POLICY \"${SLUG}_auth_update_own_member\" ON $SLUG.members FOR UPDATE TO authenticated USING (auth.uid() = user_id);
CREATE POLICY \"${SLUG}_anon_deny_email_log\" ON $SLUG.email_log FOR ALL TO anon USING (false);
CREATE POLICY \"${SLUG}_auth_deny_email_log\" ON $SLUG.email_log FOR ALL TO authenticated USING (false);
"

# Run via Supabase SQL endpoint
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SUPABASE_URL/rest/v1/rpc/exec_sql" \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": $(echo "$SCHEMA_SQL" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" 2>/dev/null)

# Fallback: try direct SQL endpoint
if [ "$RESPONSE" != "200" ] && [ "$RESPONSE" != "201" ]; then
    echo "    Trying direct SQL..."
    # Use psql or supabase CLI if available
    if command -v supabase &>/dev/null; then
        echo "$SCHEMA_SQL" | supabase db execute
    else
        echo "WARNING: Could not run schema creation via API."
        echo "Run migrations/01_schema_template.sql and 02_rls_template.sql manually,"
        echo "replacing {{SLUG}} with '$SLUG'."
        echo ""
        echo "Generated SQL saved to /tmp/${SLUG}_schema.sql"
        echo "$SCHEMA_SQL" > "/tmp/${SLUG}_schema.sql"
    fi
else
    echo "    Schema created."
fi

# --- Register site in public.sites table ---
echo "Registering site..."
SITE_CONFIG=$(python3 -c "
import json
print(json.dumps({
    'theme': '$THEME',
    'accent_1': '$ACCENT_1',
    'accent_2': '$ACCENT_2',
    'accent_3': '$ACCENT_3',
    'logo_text': '$LOGO_TEXT',
    'font_display': 'Poppins',
    'font_body': 'Inter',
}))
")
REGISTER=$(curl -s -w "\n%{http_code}" "$SUPABASE_URL/rest/v1/sites" \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "{\"slug\": \"$SLUG\", \"name\": $(echo "$NAME" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"config\": $SITE_CONFIG}")
REGISTER_CODE=$(echo "$REGISTER" | tail -1)

if [ "$REGISTER_CODE" = "201" ]; then
    echo "    Registered in sites table."
else
    echo "    WARNING: Failed to register site (HTTP $REGISTER_CODE)."
    echo "    Run manually: INSERT INTO public.sites (slug, name) VALUES ('$SLUG', '$NAME');"
fi

# --- Create admin user via Supabase Auth Admin API ---
echo "Creating admin user..."
ADMIN_RESPONSE=$(curl -s "$SUPABASE_URL/auth/v1/admin/users" \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$ADMIN_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\",
        \"email_confirm\": false,
        \"user_metadata\": {
            \"site\": \"$SLUG\",
            \"name\": \"$NAME\",
            \"is_admin\": true
        }
    }")

ADMIN_ID=$(echo "$ADMIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -n "$ADMIN_ID" ] && [ "$ADMIN_ID" != "None" ]; then
    echo "    Admin user created (ID: ${ADMIN_ID:0:8}...)."
else
    echo "    WARNING: Failed to create admin user."
    echo "    The user may already exist, or there was an auth error."
    echo "    Create the admin manually or check the error:"
    echo "    $ADMIN_RESPONSE"
fi

# --- Done ---
echo ""
echo "=== Site Created ==="
echo ""
echo "  URL:        $SITE_URL/$SLUG"
echo "  Admin:      $ADMIN_EMAIL"
echo "  Password:   $ADMIN_PASSWORD"
echo "  Login:      $SITE_URL/$SLUG/login"
echo ""
echo "Next steps:"
echo "  1. Log in with the credentials above"
echo "  2. Share $SITE_URL/$SLUG/login with people you want to invite"
echo "  3. They sign up and are automatically added as members"
echo ""
echo "To delete: DROP SCHEMA $SLUG CASCADE; DELETE FROM public.sites WHERE slug='$SLUG';"
