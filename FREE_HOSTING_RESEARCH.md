# Free Hosting Research: Python FastAPI + Vite Stack

**Date:** August 20, 2026  
**Goal:** Zero-budget deployment for Algerian business feasibility generator (Decree 26-154)

---

## TL;DR — Recommended Free Stack

| Layer | Recommended | Free Tier | Why |
|-------|------------|-----------|-----|
| **Frontend (Vite)** | Cloudflare Pages | Unlimited static, 100K req/day | Fastest, no cold starts |
| **Backend (FastAPI)** | Render | 750 hrs/mo, 512MB RAM | True persistent Python process |
| **Database (PostgreSQL)** | Neon | 0.5 GB storage | Serverless, auto-suspend, permanent free |
| **Auth** | Supabase Auth | 50K MAU | Bundled with DB if using Supabase |
| **Analytics** | Cloudflare Web Analytics | Free, unlimited | Cookieless, no GDPR banner |
| **Domain** | Free subdomain | Various providers | No cost, upgradeable later |
| **SSL** | Cloudflare | Free with any plan | Automatic |
| **WhatsApp** | Meta Cloud API | 1,000 conversations/mo | Official API, no BSP markup |

**Total monthly cost: $0**

---

## 1. Free Backend Hosting (Python/FastAPI)

### 1.1 Render (Recommended)

**Free Tier Limits:**
- 750 hours/month (enough for one 24/7 service)
- 512 MB RAM, shared CPU
- Auto-deploy from GitHub
- Free PostgreSQL database (1 GB, but **deleted after 30 days**)

**Works for this use case?** ✅ Yes — FastAPI runs as a persistent process, no cold start issues for always-on services.

**Gotchas:**
- **Spins down after 15 minutes of inactivity** — first request triggers 30-60 second cold start
- Free PostgreSQL is deleted after 30 days — use Neon instead for permanent DB
- No custom domains on free tier (use `.onrender.com` subdomain)

**Setup:**
1. Connect GitHub repo to Render
2. Create "New Web Service" → select Python
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (DATABASE_URL, etc.)

---

### 1.2 Fly.io

**Free Tier Status:** ⚠️ Free tier removed October 2024. Minimum is Hobby plan at $5/month.

**Works for this use case?** ❌ Not free anymore.

**Note:** Many 2024/2025 tutorials still reference Fly.io free tier — this is outdated.

---

### 1.3 Railway

**Free Tier Limits:**
- Trial: One-time $5 credit (30 days)
- After trial: $1/month in non-rollover credits
- 1 vCPU, 0.5 GB RAM per service
- 1 project, 3 services max

**Works for this use case?** ⚠️ Technically yes, but barely — $1/month credit covers one minimal app with no database.

**Gotchas:**
- Credits don't roll over — unused $1 resets each month
- A lightweight Python service costs ~$0.30-0.50/month, so a DB alongside will exhaust credits
- App stops immediately when credits run out
- **Not truly free after trial** — the $1/month free plan is extremely limited

**Setup:**
1. Connect GitHub repo
2. Railway auto-detects Python
3. Add PostgreSQL as a service (uses credit budget)

---

### 1.4 Vercel (Python Serverless)

**Free Tier Limits:**
- 100 GB bandwidth/month
- 1M function invocations/month
- 10 second execution timeout (free tier)
- 1 vCPU, 2GB RAM per function

**Works for this use case?** ⚠️ Only for simple stateless APIs.

**Gotchas:**
- **10 second execution timeout** — any background task, PDF generation, or email sending will be killed
- **No WebSocket support**
- **No persistent processes** — Celery workers impossible
- **FastAPI BackgroundTasks unreliable** — function may terminate before background task completes
- **Heavy cold starts** for Python (300-800ms)
- **No Docker support**
- Better for Vite frontend hosting than Python backend

**Setup:**
1. Create `api/` directory in repo root
2. Place FastAPI app in `api/index.py`
3. Add `vercel.json` with Python runtime config
4. Deploy via Vercel CLI or GitHub integration

---

### 1.5 PythonAnywhere

**Free Tier Limits:**
- 512 MB storage
- 1 web app (always-on on free tier — no sleep!)
- Shared CPU, limited bandwidth
- `*.pythonanywhere.com` subdomain

**Works for this use case?** ✅ Yes — always-on, no cold starts, beginner-friendly.

**Gotchas:**
- Limited to specific Python packages (no pip install everything)
- No SSH access on free tier
- Shared CPU can be slow
- Manual file upload (no Git integration on free tier)

---

## 2. Free Frontend Hosting (Vite/React)

### 2.1 Cloudflare Pages (Recommended)

**Free Tier Limits:**
- **Unlimited** static asset serving
- 100,000 requests/day
- 10ms CPU time per invocation
- Free SSL
- Custom domains supported
- Unmetered bandwidth

**Works for this use case?** ✅ Perfect — Vite builds to static files, Cloudflare serves them free forever.

**Gotchas:**
- No server-side rendering (not needed for Vite SPA)
- Build minutes included, no separate metering
- Static assets have free, unmetered egress on all plans

**Setup:**
1. Push Vite project to GitHub
2. Connect repo to Cloudflare Pages
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Deploy — get `your-project.pages.dev` subdomain

---

### 2.2 Netlify

**Free Tier Limits:**
- 300 credits/month (deploy = 15 credits, bandwidth = 20 credits/GB)
- ~300 MB bandwidth equivalent
- 300 build minutes/month

**Works for this use case?** ✅ Yes, but credit system is confusing and limits are tighter than Cloudflare.

**Gotchas:**
- Credit-based billing is opaque
- Bandwidth rate doubled to 20 credits/GB in April 2026
- Slower builds than Cloudflare in benchmarks

---

### 2.3 Vercel (Frontend Only)

**Free Tier Limits:**
- 100 GB bandwidth/month
- 1M edge requests/month
- 6,000 build minutes/month
- 200 projects max
- Free SSL

**Works for this use case?** ✅ Excellent for Vite frontend. Vercel is optimized for frontend hosting.

**Gotchas:**
- Best for Next.js, but works fine with Vite
- Build minutes are now credit-metered
- Overkill if you only need static hosting

---

## 3. Free Database (PostgreSQL)

### 3.1 Neon (Recommended)

**Free Tier Limits:**
- **0.5 GB storage**
- Auto-scales to 2 compute units
- **Auto-suspends when idle** (cold start ~1-5 seconds)
- No credit card required
- Permanent free tier

**Works for this use case?** ✅ Yes — serverless PostgreSQL, perfect for development and small apps.

**Gotchas:**
- **0.5 GB fills fast** with indexes, WAL, and dead tuples
- Cold start after idle (~1-5 seconds wake-up)
- No automated backups on free tier
- Connection pooling recommended (use Neon's built-in pooler)

**Setup:**
1. Sign up at neon.tech
2. Create project → get connection string
3. Use `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname`
4. Enable connection pooling for serverless apps

---

### 3.2 Supabase (Database + Auth + Storage)

**Free Tier Limits:**
- **500 MB database storage**
- 500 MB RAM (shared)
- 60 max direct connections, 200 pooler connections
- **50,000 MAU** (auth)
- 1 GB file storage
- 5 GB egress/month
- **2 active projects max**
- **Pauses after 7 days of inactivity** (30-second wake-up)

**Works for this use case?** ✅ Excellent — gives you database + auth + storage in one package.

**Gotchas:**
- **Pauses after 7 days inactivity** — set up a keep-alive ping (cron job)
- No automatic backups on free tier
- 500 MB storage limit
- 2 project limit

**Setup:**
1. Sign up at supabase.com
2. Create project → get connection string
3. Use Supabase client for auth + storage
4. Set up keep-alive: schedule a daily query to prevent pause

---

### 3.3 Aiven

**Free Tier Limits:**
- **5 GB storage** (largest free Postgres!)
- 1 vCPU, 1 GB RAM
- Single node (no failover)
- Limited connections

**Works for this use case?** ✅ Yes — largest free storage at 5 GB.

**Gotchas:**
- Single node, no redundancy
- Limited connections
- Newer provider, smaller community

---

### 3.4 Render PostgreSQL

**Free Tier Limits:**
- 1 GB storage
- 256 MB RAM
- **Deleted after 30 days** ⚠️

**Works for this use case?** ❌ Not recommended — database disappears after 30 days.

---

### 3.5 Turso (SQLite Edge)

**Free Tier Limits:**
- 500 databases
- 9 GB total storage
- 1 billion row reads/month
- 1 million row writes/month

**Works for this use case?** ⚠️ SQLite, not PostgreSQL — may not work with SQLAlchemy/PSycopg2 patterns.

**Gotchas:**
- SQLite, not PostgreSQL — different SQL dialect
- Edge-optimized, good for reads
- May require code changes

---

## 4. Free Authentication

### 4.1 Supabase Auth (Recommended)

**Free Tier Limits:**
- **50,000 MAU** (monthly active users)
- Social OAuth providers (Google, GitHub, etc.)
- Anonymous sign-ins
- Custom SMTP
- Basic MFA

**Works for this use case?** ✅ Perfect — 50K MAU is massive for a business tool.

**Gotchas:**
- No SAML/SSO on free tier
- No leaked password protection
- No session timeout controls
- Cannot remove Supabase branding from auth emails

**Setup:**
1. Enable Auth in Supabase dashboard
2. Configure providers (Email, Google, etc.)
3. Use `supabase.auth.signUp()` / `supabase.auth.signIn()`
4. Row Level Security for data access

---

### 4.2 Clerk

**Free Tier Limits:**
- **50,000 MAU**
- Social logins
- Multi-factor authentication
- User management dashboard

**Works for this use case?** ✅ Yes — generous free tier, great DX.

**Gotchas:**
- React/Next.js-first (works with vanilla JS but less polished)
- Dashboard has learning curve
- Branding on free tier

---

### 4.3 Auth0

**Free Tier Limits:**
- **25,000 MAU**
- Social connections
- Basic MFA

**Works for this use case?** ✅ Yes, but lower MAU limit than Supabase/Clerk.

**Gotchas:**
- SSO connections cost extra
- Pricing escalates quickly
- Enterprise-focused, overkill for simple apps

---

## 5. Free Analytics

### 5.1 Cloudflare Web Analytics (Recommended)

**Free Tier Limits:**
- **Unlimited** pageviews
- Cookieless
- No GDPR banner needed
- Zero-config if site is on Cloudflare

**Works for this use case?** ✅ Perfect — free, unlimited, privacy-first.

**Gotchas:**
- Page-level metrics only (no funnels, events, or per-visitor journeys)
- No conversion tracking
- Basic referral data

**Setup:**
1. If site is on Cloudflare → automatic
2. Otherwise: add single script tag to `<head>`

---

### 5.2 GoatCounter

**Free Tier Limits:**
- Free hosted for non-commercial/small sites
- Cookieless, privacy-first
- 1KB script

**Works for this use case?** ✅ Good for simple traffic counting.

**Gotchas:**
- Free plan intended for personal/small projects
- No funnel analysis
- Limited event tracking

---

### 5.3 PostHog

**Free Tier Limits:**
- ~1M events/month free
- Session replay, feature flags, funnels

**Works for this use case?** ✅ Very generous if you need product analytics.

**Gotchas:**
- Heavier than pageview-only tools
- Product analytics focus (overkill for simple sites)

---

### 5.4 Umami (Self-Hosted)

**Free Tier Limits:**
- Free open-source (MIT license)
- Unlimited sites and events when self-hosted
- Requires your own server

**Works for this use case?** ✅ If you self-host on Render/VPS.

**Gotchas:**
- You maintain the database and updates
- Requires Docker + Postgres/MySQL

---

## 6. Free Domain Options

### 6.1 Platform Subdomains (Easiest)

| Platform | Free Subdomain | Example |
|----------|---------------|---------|
| Cloudflare Pages | `*.pages.dev` | `feasibility-generator.pages.dev` |
| Render | `*.onrender.com` | `feasibility-generator.onrender.com` |
| Vercel | `*.vercel.app` | `feasibility-generator.vercel.app` |
| Netlify | `*.netlify.app` | `feasibility-generator.netlify.app` |
| Fly.io | `*.fly.dev` | `feasibility-generator.fly.dev` |

**Works for this use case?** ✅ Yes — professional enough for MVP.

### 6.2 Free Subdomain Providers

| Provider | TLDs | Notes |
|----------|------|-------|
| eu.org | `.eu.org` | Free, but registration can be slow |
| afraid.org | Various | Free subdomains, community-managed |
| duckdns.org | `.duckdns.org` | Dynamic DNS, free |

### 6.3 Freenom Alternatives

Freenom (.tk, .ml, .ga, .cf, .gq) shut down. Current options:
- **eu.org** — best free alternative, `.eu.org` subdomains
- **pp.ua** — free `.pp.ua` subdomains
- ** Various free subdomain services** — search "free subdomain provider"

**Recommendation:** Use platform subdomain (e.g., `*.pages.dev`) for simplicity, then buy a `.dz` domain ($10-15/year) when ready for production.

---

## 7. Free SSL

### 7.1 Cloudflare

**Free Tier:**
- Automatic SSL/TLS on all plans
- Universal SSL certificate
- Custom domain support

**Works for this use case?** ✅ Yes — free SSL with any Cloudflare plan.

### 7.2 Platform-Provided

All major platforms (Render, Vercel, Netlify, Cloudflare Pages) provide free SSL certificates automatically.

---

## 8. Free WhatsApp Integration

### 8.1 Meta WhatsApp Cloud API

**Free Tier Limits:**
- **1,000 conversations/month** (free)
- User-initiated conversations: ~$0.005-0.02
- Business-initiated: ~$0.02-0.08
- Template message fees apply after free tier

**Works for this use case?** ✅ Yes — 1,000 free conversations/month is sufficient for small business.

**Gotchas:**
- **Service messages will be charged starting October 2026**
- Template messages require approval
- Business verification required
- Rate limits on sending

**Setup:**
1. Create Meta Developer account
2. Set up WhatsApp Business account
3. Generate access token
4. Send messages via API:
```python
import requests

url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
payload = {
    "messaging_product": "whatsapp",
    "to": PHONE_NUMBER,
    "type": "text",
    "text": {"body": "Hello from FastAPI!"}
}
requests.post(url, json=payload, headers=headers)
```

---

## 9. Free Email (SMTP)

### 9.1 Brevo (formerly Sendinblue)

**Free Tier Limits:**
- 300 emails/day
- Unlimited contacts
- Email templates

**Works for this use case?** ✅ Yes — 300 emails/day is plenty for transactional email.

### 9.2 Mailgun

**Free Tier Limits:**
- 5,000 emails/month (first 3 months)
- Then 1,000 emails/month

**Works for this use case?** ✅ Yes for transactional emails.

### 9.3 EmailJS (Client-side)

**Free Tier Limits:**
- 200 emails/month
- No backend needed

**Works for this use case?** ⚠️ Limited but works for simple notifications.

---

## 10. Recommended Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cloudflare DNS                        │
│              (Free SSL + CDN + Analytics)                │
└─────────────┬───────────────────────┬───────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────┐   ┌─────────────────────────────┐
│   Cloudflare Pages  │   │      Render (Free Tier)     │
│   (Vite Frontend)   │   │      (FastAPI Backend)      │
│   *.pages.dev       │   │      *.onrender.com         │
└─────────────────────┘   └──────────┬──────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │    Neon PostgreSQL   │
                          │    (0.5 GB Free)     │
                          └─────────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          ▼                      ▼
                 ┌─────────────────┐   ┌─────────────────┐
                 │  Supabase Auth  │   │  Meta WhatsApp  │
                 │  (50K MAU Free) │   │  (1K convos)    │
                 └─────────────────┘   └─────────────────┘
```

---

## 11. Quick Setup Checklist

### Phase 1: Database (5 min)
- [ ] Sign up at neon.tech
- [ ] Create PostgreSQL project
- [ ] Copy connection string
- [ ] Run initial migrations

### Phase 2: Backend (10 min)
- [ ] Push FastAPI code to GitHub
- [ ] Connect repo to Render
- [ ] Set environment variables (DATABASE_URL, WHATSAPP_TOKEN, etc.)
- [ ] Deploy and verify API works

### Phase 3: Frontend (5 min)
- [ ] Push Vite code to GitHub
- [ ] Connect repo to Cloudflare Pages
- [ ] Set build command: `npm run build`
- [ ] Set output: `dist`
- [ ] Deploy and verify frontend loads

### Phase 4: Domain & SSL (5 min)
- [ ] Add custom domain to Cloudflare Pages (or use `*.pages.dev`)
- [ ] Add CNAME record pointing to backend
- [ ] Verify SSL is working

### Phase 5: Services (10 min)
- [ ] Enable Supabase Auth (if using Supabase for DB too)
- [ ] Set up Meta WhatsApp Cloud API
- [ ] Add Cloudflare Web Analytics script
- [ ] Configure Brevo for transactional email

---

## 12. Cost Comparison: Free vs Paid

| Component | Free Stack | Cheapest Paid |
|-----------|-----------|---------------|
| Backend | Render ($0) | Render Starter ($7/mo) |
| Frontend | Cloudflare Pages ($0) | Vercel Pro ($20/mo) |
| Database | Neon ($0) | Neon Launch ($19/mo) |
| Auth | Supabase Auth ($0) | Clerk Pro ($25/mo) |
| Analytics | Cloudflare ($0) | Plausible Cloud ($9/mo) |
| Domain | Free subdomain ($0) | .com domain ($12/yr) |
| SSL | Cloudflare ($0) | Included with hosting |
| WhatsApp | Meta API ($0 for 1K) | $0.02-0.08/conversation |
| **Total** | **$0/month** | **~$70-100/month** |

---

## 13. Critical Gotchas Summary

1. **Render spins down after 15 min** — first request has 30-60s cold start
2. **Supabase pauses after 7 days** — set up keep-alive cron
3. **Neon 0.5 GB fills fast** — optimize queries, archive old data
4. **Railway $1/month free is barely usable** — one tiny app, no DB
5. **Fly.io free tier is gone** — don't follow old tutorials
6. **Vercel 10s timeout kills Python** — not suitable for PDF generation
7. **Render free DB deleted in 30 days** — use Neon instead
8. **WhatsApp service messages will cost money Oct 2026** — plan accordingly

---

## 14. Migration Path (When You Outgrow Free)

| When | What | How |
|------|------|-----|
| > 0.5 GB data | Upgrade Neon | $19/mo Launch plan |
| > 750 hrs/month | Upgrade Render | $7/mo Starter plan |
| > 50K users | Upgrade Supabase | $25/mo Pro plan |
| Need custom domain | Buy `.dz` domain | ~$10-15/year |
| Need email deliverability | Upgrade Brevo | $9/mo Starter |

**Migration is easy:** `pg_dump` → `pg_restore` → update connection string → redeploy. No lock-in.

---

*Research compiled from official pricing pages and independent benchmarks (August 2026)*
