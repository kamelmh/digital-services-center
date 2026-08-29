"""RLS enforcement — real Postgres probe as dsc_app. Skipped without PG env.

This is the test Sprint 6 exists to create. test_tenant_isolation.py (17 tests)
runs on SQLite and only proves application-layer .filter(tenant_id==). This
file connects as the non-superuser `dsc_app` that 003_rls_policies.sql §0
creates, proves FORCE RLS is on, and shows a foreign-tenant row is invisible
to a query issued after SET LOCAL app.current_tenant_id = <other tenant>.

Run locally: DATABASE_URL=postgresql://dsc_app:dsc_app_local@localhost:5432/neondb \
             DSC_RLS_TEST_DATABASE_URL=postgresql://dsc_app:dsc_app_local@localhost:5432/neondb \
             pytest tests/test_rls_enforcement.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text

pytestmark = pytest.mark.skipif(
    not os.getenv("DSC_RLS_TEST_DATABASE_URL"),
    reason="Set DSC_RLS_TEST_DATABASE_URL to a dsc_app PostgreSQL connection string",
)


def test_connected_as_dsc_app_not_superuser() -> None:
    engine = create_engine(os.environ["DSC_RLS_TEST_DATABASE_URL"], pool_pre_ping=True)
    with engine.begin() as conn:
        user = conn.execute(text("SELECT current_user")).scalar_one()
        assert user == "dsc_app", f"expected dsc_app (non-superuser), got {user}"


def test_force_rls_is_on_for_all_four_tables() -> None:
    engine = create_engine(os.environ["DSC_RLS_TEST_DATABASE_URL"], pool_pre_ping=True)
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                "SELECT relname, relrowsecurity, relforcerowsecurity "
                "FROM pg_class WHERE relname IN ('users','dossiers','jobs','checkouts')"
            )
        ).fetchall()
        by_name = {r[0]: (r[1], r[2]) for r in rows}
        assert set(by_name) == {"users", "dossiers", "jobs", "checkouts"}, by_name
        for table in ("users", "dossiers", "jobs", "checkouts"):
            relrowsecurity, relforcerowsecurity = by_name[table]
            assert relrowsecurity is True, f"{table} RLS not enabled"
            assert relforcerowsecurity is True, f"{table} FORCE RLS not set"


def test_cross_tenant_dossier_invisible_to_other_tenant() -> None:
    engine = create_engine(os.environ["DSC_RLS_TEST_DATABASE_URL"], pool_pre_ping=True)
    tenant_a = str(uuid.uuid4())
    tenant_b = str(uuid.uuid4())
    dossier_id = str(uuid.uuid4())

    with engine.begin() as conn:
        # Seed one dossier owned by A — insert as "A" so RLS lets it in.
        conn.execute(text("SELECT set_config('app.current_tenant_id', :tid, true)"), {"tid": tenant_a})
        # Re-read UUID as text comparison (id::text = current_setting(...)) — ensure format.
        conn.execute(
            text(
                "INSERT INTO users (id, email, password_hash, subscription) "
                "VALUES (:id, :email, 'x', 'free') ON CONFLICT (id) DO NOTHING"
            ),
            {"id": tenant_a, "email": f"rls-a-{tenant_a[:8]}@example.test"},
        )
        conn.execute(
            text("INSERT INTO dossiers (id, tenant_id, project_name, status) VALUES (:id, :tid, 'Sprint 6 probe', 'draft')"),
            {"id": dossier_id, "tid": tenant_a},
        )

    # Read back as B — must see zero rows for A's dossier.
    with engine.begin() as conn:
        conn.execute(text("SELECT set_config('app.current_tenant_id', :tid, true)"), {"tid": tenant_b})
        count = conn.execute(
            text("SELECT count(*) FROM dossiers WHERE id = :id"),
            {"id": dossier_id},
        ).scalar_one()
        assert count == 0, f"dossier {dossier_id} leaked to tenant {tenant_b}"
        plain = conn.execute(text("SELECT count(*) FROM dossiers")).scalar_one()
        assert plain == 0, f"unfiltered dossiers leaked to tenant {tenant_b}: {plain}"

    # Owner A can still see its own row.
    with engine.begin() as conn:
        conn.execute(text("SELECT set_config('app.current_tenant_id', :tid, true)"), {"tid": tenant_a})
        own = conn.execute(text("SELECT count(*) FROM dossiers WHERE id = :id"), {"id": dossier_id}).scalar_one()
        assert own == 1

    # Cleanup (bypass RLS by resetting txn to postgres-owner; optional — rollback-scoped seed is fine).
    # Leave the row; next run uses different UUIDs. FK will orphan on user but deduped by ON CONFLICT.
