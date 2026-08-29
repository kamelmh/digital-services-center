# DSC Roadmap — Single Strategy Document

> Consolidates `STRATEGIC_ANALYSIS.md`, `BUSINESS_PLAN.md`, `ALGERIAN_ADMIN_SERVICES.md`, `FACEBOOK_PAGE_SETUP.md`, and `knowledge_base/gaps_analysis.md` next-steps. Replaces 5 stale strategy docs per `DSC_DEEP_ASSESSMENT.md` §8. HEAD `2d4168d` (Sprint 9).

## 1. Current State

DSC is MVP-complete and sellable today: **20 form generators** (G12/G12bis/G13/G1/G4/G4-rental/G8/G11/G29/G50/G15/G51 + CNRC F1/F2/DAS/SECU01/NIS/ANAE/CASNOS×2) plus **12 document generators** (feasibility 9-part Decree 26-154, NESDA 0%/7y/1.5y, business plan, BMC, market/mktg/projections/invoice/CV/cover/social/tax) share a unified pipeline `dataclass → calculate_*() → generate_*_html()`. All 2026 rates are centralized in `policy_constants.py:14-50` (`TAX_YEAR=2026`, `TVA 19/9` `policy_constants.py:16-17`, `IBS 19/23/26` `policy_constants.py:19-21`, `IFU 5/12/0.5` `policy_constants.py:23-25`, `CNAS 25.5/9` `policy_constants.py:27-29`, `SNMG 24k` `policy_constants.py:30`, `CASNOS 15% min 3k` `policy_constants.py:31-32`, `VAN 12%` `policy_constants.py:34`, `NESDA 0%/7y/1.5y` `policy_constants.py:37-40`, `IRG_ANNUAL 240k/480k/960k/1.92M/3.84M` `policy_constants.py:43-50` → `IRG_MONTHLY` via `annual_to_monthly_brackets()`). Verification is non-self-affirming: `verify_rates.py:REVIEWED_2026_IRG_ANNUAL` proves `policy_constants == reviewed snapshot`, then generators == `policy_constants` — **67/67 `verify_rates.py --strict`**, **164 tests** (CI `ci.yml:49-57`), RLS enforced by `dsc_app` under `FORCE ROW LEVEL SECURITY`, Chargily live DZD (`pay.chargily.dz/test|live/api/v2/checkouts` `billing.py:99-107`), Pages artifact narrowed to `docs/` only (`deploy.yml:path='./docs'`).

## 2. Done — Sprints 1–9

| Sprint | Commit | One-line |
|--------|--------|----------|
| 1 | `4d30e54` | Doc sync 20 generators, G11/G29 IRG unified (240k/480k/960k/1.92M/3.84M + 20k/40k/80k/160k/320k) |
| 2 | `0936d6b` | Chargily activation, quota display, `billing/mock-pay` local fallback |
| 3 | `f1ca45f` | Pricing for 20 forms (30 services/4 bundles), SEO `knowledge_base/forms/catalog.md` |
| 4 | `c948062` | Tenant isolation hardening (JWT→tenant, RLS GUC `app.current_tenant_id`) |
| 5 | `9b5557d`+`dbd5045` | CI hardening (PG service, RLS migrate) + admin cross-tenant view (`is_admin` bypass, `GET /v1/dossiers/me`) |
| 6 | `36233c7`+`40b7987` | RLS enforcement: `dsc_app` role + `FORCE` + real PG probe `test_rls_enforcement.py` (closes 2026-08-24 gap) |
| 7 | `c52b44a` | Chargily live cutover: 502 on live failure, `X-Chargily-Signature` HMAC pin, `payment_url` redirect |
| 8 | `59f228c`+`6c90dfc` | `policy_constants.py` single source, 15 generators aliased, `verify_rates` 38→67 non-self-affirming |
| 9 | `7c4ac99`+`2d4168d` | `verify_rates --strict` gate in CI + Pages `path: '.' → './docs'` + verifier icon fix |

Pre-Sprint 9 history: Batch 1–3 generators (G13/CNRC/DAS/SECU/ANAE/NIS/G4-rental/G15), offline fallback `offline_templates.py`, Arabic Tahoma PDF, VAN/TRI single-source `financial_calculators.py` — see `UPDATES.md` 2026-08-20→22 and `DSC_DEEP_ASSESSMENT.md` §6.2.

## 3. Next — Sprints 10–12 Candidates

All items are free/open-source; none block current offline + free-tier SaaS sales (Lane C — Hybrid, `DSC_DEEP_ASSESSMENT.md` §6.1).

| # | Candidate | Source | Effort | Impact | Notes |
|---|-----------|--------|--------|--------|-------|
| 10a | **Public-site guard** — wire `check_public_site.py` in `deploy.yml` before `upload-pages-artifact` | Constants Guide §4 | S (1h) | High | Artifact boundary is `path: './docs'`; scan is backstop for accidental secrets inside `docs/`. Add `python check_public_site.py docs` step; fail on 1. |
| 10b | **SEO distribution** — 20 form pages + sitemap on `docs/` (GitHub Pages) | Gaps closed, distribution gap remains | M (1 day) | High | One page per generator (rate table + CTA → `pricing_calculator.py` `wa.me`); add `sitemap.xml` + `tax-forms.html` index. Organic discovery before paid ads. |
| 10c | **Admin support tooling** — export `is_admin` cleanly (`GET /v1/dossiers/me` already exists) + admin audit log | Sprints 5–6 `is_admin` GUC | S (2h) | Med | Prove admin scope in UI; add `X-Request-ID` + tenant on webhook logs (`billing.py:206-212`). No new infra. |
| 11a | **Deadline reminders** — DGI/CNAS calendar (DAS Jan31, G12 Jun30, G13 Apr30) | `knowledge_base/deadlines/timeline.md` | S (2h) | High | `apscheduler` + `smtplib`/Gmail free; drives repeat purchases. |
| 11b | **Bundle/pricing polish** — NIF+RC+NIS starter pack already in `f1ca45f`; add CASNOS/ANAE kit | `BUSINESS_PLAN.md` Tier 3 | S (30m) | Med | Update `pricing_calculator.py:SERVICES` (devis amounts ≠ regulated rates). |
| 12 | **Low-priority gaps** — AS1/AS8/Certificat Négatif (CNAS employee / CNRC name check) | `gaps_analysis.md:73-80` | S–M (2–4h each) | Low | All P1/P2/P3 gaps filled (13 generators built Sprint 1); these 3 remain low willingness-to-pay — defer until SEO lane converts. Do not build mobile app/microservices/K8s (`DSC_DEEP_ASSESSMENT.md` §6.3). |

Ordering: **10a → 10b → 10c → 11a → 11b → 12**. 10a is a one-line CI safety net; do it with any next PR.

## 4. Invariants — Do Not Break (verbatim from `DSC_DEEP_ASSESSMENT.md` §8)

1. **VAN is always 12%** (`FinancialCalculators.van(discount_rate=0.12)`) — not 10%. NESDA dossier was wrong at 10% before 2026-08-19.
2. **IRG is always 6 tranches** (240K/480K/960K/1.92M/3.84M at 0/23/27/30/33/35) — annual DZD; G29 monthly is `annual/12` (20K/40K/80K/160K/320K @ 0/23/27/30/33/35, `g29_irg_salaires_generator.py:38`).
3. **IFU is 5% production / 12% services / 0.5% auto-entrepreneur** — ANAE had them swapped before this session.
4. **IBS is 19% production / 23% BTP-tourism / 26% commerce-services** — 3 tiers, not 2.
5. **CNAS is 25.5% employer + 9% employee = 34.5% total** — not 26% (that includes 0.5% œuvres sociales).
6. **CASNOS is 15% of CA, min 3,000 DA/month** — not flat 43,200. Flat is ANAE auto-entrepreneur variant.
7. **NESDA is 0% interest / 7y repayment / 1.5y grace** — not 2%/12y.
8. **`fastapi==0.110.3` must not be upgraded** without fixing `_IncludedRouter` in SaaS routers.
9. **Tenant isolation is DB-enforced by `dsc_app` (non-owner) under `FORCE ROW LEVEL SECURITY`, verified against real Postgres** (`003_rls_policies.sql` §§0-1, `ci.yml` `dsc_app:dsc_app_local@localhost:5432/neondb`, `tests/test_rls_enforcement.py` cross-tenant probe). Superuser `postgres:postgres` bypasses every policy by Postgres design — never point `DATABASE_URL` at it, and never drop `FORCE` (Neon production `DATABASE_URL` must be `postgresql://dsc_app:<password>@<host>/neondb?sslmode=require` — see `PRODUCTION_CHECKLIST.md`).
10. **Chargily is the live DZD gateway (BaridiMob/CIB/Dahabiya), always DZD-only, always `payment_url` redirect, always webhook-verified** (`billing.py:99-107` `pay.chargily.dz/test|live/api/v2/checkouts`, `billing.py:171-182` `X-Chargily-Signature` HMAC-sha256, `billing.py:239-258` plan/amount/currency/tenant + idempotency). `mock` remains as `?gateway=mock` local fallback; a live Chargily failure surfaces as 502 (not silent mock fallback) and a webhook with bad/no signature is 401 when `gateway==chargily` (tests: `test_chargily_live_rejects_mock_webhook_bypass`).
11. **2026 rates have a single source of truth — `policy_constants.py`** (`TAX_YEAR=2026`, `IBS/TVA/IFU/CNAS/CASNOS/SNMG/VAN/NESDA/IRG_ANNUAL→IRG_MONTHLY` with `annual_to_monthly_brackets()`). No regulated literal lives outside the canonical file or the reviewed snapshot in `verify_rates.py:REVIEWED_2026_IRG_ANNUAL` — `verify_rates.py` proves `policy_constants == REVIEWED` (non-self-affirming) and separately that every generator alias equals `policy_constants`; an edit to the canonical file alone cannot self-affirm (Guide `proposed→done` 2026-08-29, boundary: G29 `annual/12` and CNAS component table intentionally unchanged).

## 5. Production Cutover Checklist (from `PRODUCTION_CHECKLIST.md` — one-timers)

### Sprint 6 — Neon RLS isolation
- [ ] On Neon branch: run the `DO $$ CREATE ROLE dsc_app … $$` preamble + `GRANT` block from `apps/api/migrations/003_rls_policies.sql` §§0-1 (creates `dsc_app`, scoped GRANTs, `FORCE ROW LEVEL SECURITY` ×4).
- [ ] In Render (dsc-api): set `DATABASE_URL` to `postgresql://dsc_app:<password>@<neon-host>/neondb?sslmode=require` (never `postgres:postgres` — superuser bypasses RLS by design).
- [ ] Verify: `psql $PG_DSN_DSC_APP -c "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('users','dossiers','jobs','checkouts');"` and cross-tenant probe `tests/test_rls_enforcement.py`.

### Sprint 7 — Chargily DZD live
- [ ] In Chargily dashboard: set `webhook_endpoint = https://dsc-api-vsex.onrender.com/billing/webhook`, copy signing secret.
- [ ] In Render (dsc-api): set `DSC_CHARGILY_KEY` (`live_…` or `test_…` — test key auto-routes to `pay.chargily.dz/test/api/v2/checkouts`), `DSC_CHARGILY_SECRET`, `DSC_BILLING_WEBHOOK_SECRET` (= Chargily signing secret).
- [ ] Flip `DSC_BILLING_GATEWAY` `mock → chargily` (live failure now 502, webhook bad signature 401 when `gateway==chargily`; `?gateway=mock` still bypasses HMAC for local dev `billing.py:176-177`).
- [ ] Smoke test: `POST /billing/checkout` → follow `payment_url` → BaridiMob/CIB/Dahabiya pay → `billing/success?checkout_id=…` polls `/billing/me`.

> Weeks 1–8 VPS/domain/analytics in `PRODUCTION_CHECKLIST.md` are valid for Oracle/Hetzner self-host path (`DSC_DEEP_ASSESSMENT.md` §5.2 Path B) — sequence only if free-tier limits are hit.

---
*Teams: offline exe + WhatsApp/CCP closes first sales this week; SaaS compounds after cutover. Next doc to read after this: `DSC_DEEP_ASSESSMENT.md` then `UPDATES.md` per `AGENTS.md` protocol.*
