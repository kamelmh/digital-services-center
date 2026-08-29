-- Migration 003: Row-Level Security policies for tenant isolation
-- Run AFTER 001_create_tables.sql and 002_add_checkout_table.sql
-- Requires: tenant.py sets `app.current_tenant_id` via set_config() before each request

BEGIN;

-- ============================================================================
-- 1. Enable RLS on all tenant-scoped tables
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE dossiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkouts ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. Users table — tenants can only see their own row
-- ============================================================================

CREATE POLICY users_tenant_isolation ON users
    FOR ALL
    USING (id::text = current_setting('app.current_tenant_id', true))
    WITH CHECK (id::text = current_setting('app.current_tenant_id', true));

-- ============================================================================
-- 3. Dossiers table — tenants can only see their own dossiers
-- ============================================================================

CREATE POLICY dossiers_tenant_isolation ON dossiers
    FOR ALL
    USING (tenant_id::text = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));

-- ============================================================================
-- 4. Jobs table — tenants can only see their own jobs
-- ============================================================================

CREATE POLICY jobs_tenant_isolation ON jobs
    FOR ALL
    USING (tenant_id::text = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));

-- ============================================================================
-- 5. Checkouts table — tenants can only see their own checkouts
-- ============================================================================

CREATE POLICY checkouts_tenant_isolation ON checkouts
    FOR ALL
    USING (tenant_id::text = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));

-- ============================================================================
-- 6. Admin bypass policy — allows admin users to access all rows
--    Requires: users table has is_admin BOOLEAN column (default false)
-- ============================================================================

-- Add is_admin column if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false;

-- Admin bypass policies (created AFTER tenant isolation policies so they take precedence)
-- PostgreSQL evaluates policies in order; the first matching ALLOW policy grants access.

DROP POLICY IF EXISTS users_admin_bypass ON users;
CREATE POLICY users_admin_bypass ON users
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users admin_check
            WHERE admin_check.id::text = current_setting('app.current_tenant_id', true)
            AND admin_check.is_admin = true
        )
    );

DROP POLICY IF EXISTS dossiers_admin_bypass ON dossiers;
CREATE POLICY dossiers_admin_bypass ON dossiers
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users admin_check
            WHERE admin_check.id::text = current_setting('app.current_tenant_id', true)
            AND admin_check.is_admin = true
        )
    );

DROP POLICY IF EXISTS jobs_admin_bypass ON jobs;
CREATE POLICY jobs_admin_bypass ON jobs
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users admin_check
            WHERE admin_check.id::text = current_setting('app.current_tenant_id', true)
            AND admin_check.is_admin = true
        )
    );

DROP POLICY IF EXISTS checkouts_admin_bypass ON checkouts;
CREATE POLICY checkouts_admin_bypass ON checkouts
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users admin_check
            WHERE admin_check.id::text = current_setting('app.current_tenant_id', true)
            AND admin_check.is_admin = true
        )
    );

-- ============================================================================
-- 7. Verification query (run after migration to confirm RLS is active)
-- ============================================================================
-- SELECT schemaname, tablename, rowsecurity, forcerowsecurity
-- FROM pg_tables
-- WHERE tablename IN ('users', 'dossiers', 'jobs', 'checkouts');

COMMIT;
