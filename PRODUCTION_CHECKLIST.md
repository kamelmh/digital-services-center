# DSC Production Checklist

## Sprint 6 — RLS isolation (Neon, one-time) — done `40b7987`, CI green
- [x] Migration `003_rls_policies.sql` §0 creates `dsc_app` role + scoped GRANT + `FORCE ROW LEVEL SECURITY` ×4
- [x] CI splits DSN: `DATABASE_URL` (alembic=`postgres`), `DSC_RLS_TEST_DATABASE_URL`+`PG_DSN_DSC_APP`=`dsc_app:dsc_app_local@localhost:5432/neondb`
- [x] `tests/test_rls_enforcement.py` (3 PG-only proofs) + webhook HMAC fix (`app.is_admin` GUC avoids `users` self-recursion under FORCE)
- [ ] **Manual (prod Neon, one-time):** run the `DO $$ CREATE ROLE dsc_app … $$` preamble + `GRANT` block of `003_rls_policies.sql` on the Neon branch, then update the API service's `DATABASE_URL` to `postgresql://dsc_app:<password>@<neon-host>/neondb?sslmode=require`

## Sprint 7 — Chargily live cutover (The DZD sprint) — `mock → chargily`
- [ ] In Chargily dashboard: set `webhook_endpoint = https://dsc-api-vsex.onrender.com/billing/webhook`, copy signing secret
- [ ] In Render (dsc-api): set `DSC_CHARGILY_KEY` (`live_…` or `test_…`), `DSC_CHARGILY_SECRET`, `DSC_BILLING_WEBHOOK_SECRET` (= Chargily signing secret)
- [ ] In Render: flip `DSC_BILLING_GATEWAY` `mock → chargily` (tests: `test_chargily_live_rejects_mock_webhook_bypass` pins HMAC; a live Chargily failure now raises `502`, not silent mock fallback)
- [ ] Smoke test: `POST /billing/checkout` (test key hits `pay.chargily.dz/test/api/v2/checkouts`, live key hits `.../api/v2/checkouts`) → follow `payment_url` → BaridiMob/CIB/Dahabiya pay → `billing/success?checkout_id=…` polls `/billing/me`
- [ ] Local dev stays mock: `?gateway=mock` or `DSC_BILLING_GATEWAY=mock` still bypasses HMAC (`billing.py:176-177`)

---

## Week 1: Infrastructure
- [ ] Buy domain (dsc-dz.com or similar)
- [ ] Register at Hetzner, create CX32 VPS (Falkenstein)
- [ ] Install Docker + docker-compose
- [ ] Set up Cloudflare (free tier)
- [ ] Point domain to VPS IP
- [ ] Install Nginx + certbot
- [ ] Get SSL certificate
- [ ] Basic Nginx config (reverse proxy to app)

## Week 2: Database & Auth
- [ ] Design database schema (users, clients, orders, documents, payments)
- [ ] Install PostgreSQL
- [ ] Set up Alembic migrations
- [ ] Implement user auth (JWT + bcrypt)
- [ ] Add role-based access (admin, operator, client)
- [ ] Create admin dashboard

## Week 3: Payment Flow
- [ ] Generate BaridiMob QR codes
- [ ] Create manual confirmation flow
- [ ] Build invoice PDF generator
- [ ] Add payment status tracking
- [ ] Create revenue report

## Week 4: Document Pipeline
- [ ] Test Arabic PDF generation on server
- [ ] Add document versioning
- [ ] Add watermarks to previews
- [ ] Build batch export (ZIP)
- [ ] Wire quality scoring

## Week 5: Notifications
- [ ] Set up WhatsApp Business API
- [ ] Create message templates
- [ ] Add order confirmation flow
- [ ] Add payment confirmation
- [ ] Add document ready notification

## Week 6: Analytics & Monitoring
- [ ] Install Umami (self-hosted)
- [ ] Set up Sentry error tracking
- [ ] Add UptimeRobot monitoring
- [ ] Build admin metrics dashboard
- [ ] Set up daily backups

## Week 7: Polish
- [ ] Write privacy policy
- [ ] Write terms of service
- [ ] Test invoice compliance (DGI)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Load testing

## Week 8: Launch
- [ ] Soft launch (10 clients)
- [ ] Gather feedback
- [ ] Fix issues
- [ ] Full launch
- [ ] Announce on social media

---

## Quick Commands

```bash
# Deploy to VPS
ssh root@your-vps-ip
git clone https://github.com/kamelmh/digital-services-center.git
cd digital-services-center
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f app

# Update
git pull
docker-compose up -d --build

# Backup
pg_dump -U postgres dsc > backup.sql
rclone copy backup.sql b2:dsc-backups/
```

## Cost Tracking

| Item | Cost | Date | Status |
|------|------|------|--------|
| Domain | $37-100 | | |
| VPS | €6.80/mo | | |
| WhatsApp | ~$1/100 msgs | | |
| **Total** | **~€10/mo** | | |
