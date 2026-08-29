-- Migration 003: Row-Level Security policies for tenant isolation
-- Run AFTER 001_create_tables.sql and 002_add_checkout_table.sql
-- Requires: tenant.py sets `app.current_tenant_id` via set_config() before each request

BEGIN;

-- ============================================================================
-- 0. Least-privilege application role (no RLS bypass) — idempotent
--    Production DATABASE_URL should connect as dsc_app; CI's postgres:postgres
--    superuser bypasses every policy below unless FORCE is set (Step 7).
--    Neon manual step: create dsc_app there once; see PRODUCTION_CHECKLIST.md.
-- ============================================================================

DO $$ BEGIN
    CREATE ROLE dsc_app WITH LOGIN PASSWORD 'dsc_app_local';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

GRANT USAGE ON SCHEMA public TO dsc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users, dossiers, jobs, checkouts TO dsc_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dsc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO dsc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dsc_app;

-- ============================================================================
-- 1. Enable RLS + FORCE on all tenant-scoped tables
--    FORCE closes the owner/superuser bypass; every role including the table
--    owner is now bound by policy. Application defense-in-depth (.filter(...))
--    remains in dossiers.py:128 for SQLite and as belt-and-suspenders.
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE dossiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkouts ENABLE ROW LEVEL SECURITY;

ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE dossiers FORCE ROW LEVEL SECURITY;
ALTER TABLE jobs FORCE ROW LEVEL SECURITY;
ALTER TABLE checkouts FORCE ROW LEVEL SECURITY;

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
--    FORCE RLS makes every table policy-bound, including `users`. A policy
--    that queries `users` inside its USING would recurse infinitely. The
--    bypass therefore checks the transaction-local GUC `app.is_admin`
--    (= 'true' for admins, set by require_tenant_user and _set_tenant_context_with_admin).
--    `current_setting(..., true)` yields NULL if unset → bypass stays false.
-- ============================================================================

-- Add is_admin column if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false;

DROP POLICY IF EXISTS users_admin_bypass ON users;
CREATE POLICY users_admin_bypass ON users
    FOR ALL
    USING (current_setting('app.is_admin', true) = 'true');

DROP POLICY IF EXISTS dossiers_admin_bypass ON dossiers;
CREATE POLICY dossiers_admin_bypass ON dossiers
    FOR ALL
    USING (current_setting('app.is_admin', true) = 'true');

DROP POLICY IF EXISTS jobs_admin_bypass ON jobs;
CREATE POLICY jobs_admin_bypass ON jobs
    FOR ALL
    USING (current_setting('app.is_admin', true) = 'true');

DROP POLICY IF EXISTS checkouts_admin_bypass ON checkouts;
CREATE POLICY checkouts_admin_bypass ON checkouts
    FOR ALL
    USING (current_setting('app.is_admin', true) = 'true');

-- ============================================================================
-- 7. Verification query (run after migration to confirm RLS is active)
-- ============================================================================
-- SELECT schemaname, tablename, rowsecurity, forcerowsecurity
-- FROM pg_tables
-- WHERE tablename IN ('users', 'dossiers', 'jobs', 'checkouts');

COMMIT;
