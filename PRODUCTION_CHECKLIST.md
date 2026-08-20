# DSC Production Checklist

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
