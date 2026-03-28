"""
Pytest configuration — mock external services for unit tests.
"""
import os
import pytest

# Set env vars before any imports that read them
os.environ.setdefault('SUPABASE_URL', 'http://localhost:54321')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test_service_key')
os.environ.setdefault('SUPABASE_ANON_KEY', 'test_anon_key')
os.environ.setdefault('RESEND_API_KEY', 'test_resend_key')
os.environ.setdefault('CRON_SECRET', 'test_cron_secret')
os.environ.setdefault('SITE_URL', 'http://localhost:3000')
os.environ.setdefault('ADMIN_EMAIL', 'admin@test.com')
os.environ.setdefault('EMAIL_FROM', 'Test <noreply@test.com>')
