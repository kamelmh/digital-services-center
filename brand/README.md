# DSC Canva Workflow

## What This Is

Step-by-step guide to create professional DSC social media content using Canva (free tier) with our existing logo assets.

## The Problem

Our Python-generated logos are garbage (wrong geometry, missing text). The REAL logos already exist:
- `logo-hexagon-clean.png` — Professional MK hexagon badge (use this)
- `images/download.png` — Clean flat MK monogram (use this)

## The Solution

Use Canva web (free) to create social media content with the real logos.

---

## PART 1: Canva Web Workflow (Free, No Code)

### Step 1: Create Canva Account
1. Go to https://www.canva.com
2. Sign up with Google or email
3. Free tier is enough for everything we need

### Step 2: Upload Brand Assets
1. Click "Brand" in left sidebar → "Brand Kit"
2. Create kit named "DSC"
3. Upload colors:
   - Navy: #0A1628
   - Gold: #D4AF37
   - White: #FFFFFF
4. Upload logos:
   - `C:\Users\Admin\projects\active\digital-services-center\assets\images\logo-hexagon-clean.png`
   - `C:\Users\Admin\projects\active\digital-services-center\images\download.png`
5. Upload fonts (or use free alternatives):
   - Space Grotesk (Google Fonts, free)
   - Inter (Google Fonts, free)

### Step 3: Create Templates

#### Facebook Profile Picture
1. Click "Create a design" → "Facebook Profile Picture"
2. Dimensions: 170x170px (auto-set)
3. Add navy background (#0A1628)
4. Drag `logo-hexagon-clean.png` to center
5. Resize to fit with padding
6. Download as PNG

#### Facebook Cover Photo
1. Click "Create a design" → "Facebook Cover"
2. Dimensions: 820x312px (auto-set)
3. Add navy background
4. Left side: Drag flat MK logo (`images/download.png`)
5. Right side: Add text "DIGITAL SERVICES CENTER"
6. Below: Add "FEASIBILITY • AUTOMATION • TRAINING" in gold
7. Download as PNG

#### Social Media Post (1080x1080)
1. Click "Create a design" → "Instagram Post"
2. Dimensions: 1080x1080px
3. Template layout:
   ```
   [Top-right: Small MK logo]
   [Left: Gold accent bar]
   [Center: Big headline]
   [Below: Subtitle in gold]
   [Bottom: Gold bar with company name]
   ```
4. Create 7 versions:
   - About Us
   - Feasibility Studies
   - Business Automation
   - Professional Training
   - Services & Pricing
   - Contact Us
   - Testimonial/Case Study

### Step 4: Download and Organize
1. Download all designs as PNG
2. Save to: `C:\Users\Admin\projects\active\digital-services-center\assets\social\canva\`
3.命名规则:
   - `dsc-profile-400.png`
   - `dsc-cover-1584.png`
   - `dsc-post-about-1080.png`
   - `dsc-post-feasibility-1080.png`
   - etc.

---

## PART 2: Canva CLI Workflow (For Developers)

### Prerequisites
- Node.js 22+ (already installed)
- Canva CLI: `@canva/cli@2.8.1` (already installed)
- Canva account (free tier works)

### Login
```bash
canva login
```
Opens browser for OAuth. One-time setup.

### Existing App Project
Location: `C:\Users\Admin\projects\active\digital-services-center\dsc-designs\`

This is a Canva app that can:
- Read design content
- Write design content
- Create designs programmatically

### Start Development Server
```bash
cd C:\Users\Admin\projects\active\digital-services-center\dsc-designs
npm start
```
Opens Canva editor with your app loaded.

### Preview App
```bash
canva apps preview
```

### Run Diagnostics
```bash
canva apps doctor
```

---

## PART 3: Template Specifications

### Color Palette (Use in Canva)
| Name | Hex | Usage |
|------|-----|-------|
| Navy | #0A1628 | Primary backgrounds |
| Gold | #D4AF37 | Accents, CTAs |
| White | #FFFFFF | Reversed text |
| Paper | #F5F5F0 | Document backgrounds |

### Typography (Use in Canva)
| Font | Weight | Usage |
|------|--------|-------|
| Space Grotesk | Bold (700) | Headlines, logo text |
| Inter | Regular (400) | Body text |
| Inter | Medium (500) | Subheadings |

### Dimensions Quick Reference
| Asset | Width | Height | Format |
|-------|-------|--------|--------|
| Facebook Profile | 170px | 170px | PNG |
| Facebook Cover | 820px | 312px | PNG |
| Instagram Post | 1080px | 1080px | PNG |
| Instagram Story | 1080px | 1920px | PNG |
| LinkedIn Profile | 400px | 400px | PNG |
| LinkedIn Cover | 1584px | 396px | PNG |
| Twitter Profile | 400px | 400px | PNG |
| Twitter Header | 1500px | 500px | PNG |

### Post Content Templates

#### Post 1: About Us
```
Headline: DIGITAL SERVICES CENTER
Subtitle: Feasibility • Automation • Training
Body:
- Feasibility Studies & Business Plans
- Business Automation & AI Solutions
- Professional Training & Consulting
Footer: kamelmahi71@gmail.com | +213 676 77 38 92
```

#### Post 2: Feasibility Studies
```
Headline: FEASIBILITY STUDIES
Subtitle: From Idea to Funded Business
Body:
- Diagnostic Express: 3,000 DZD
- Pre-Feasibility: 8,000 DZD
- Complete Study: 15,000 DZD
- Bank Dossier: 12,000 DZD
```

#### Post 3: Business Automation
```
Headline: BUSINESS AUTOMATION
Subtitle: Excel • VBA • Python • AI
Body:
- VBA Macros & Automation
- Python Data Pipelines
- AI-Powered Dashboards
- Inventory Management Systems
```

#### Post 4: Professional Training
```
Headline: PROFESSIONAL TRAINING
Subtitle: Skills That Pay The Bills
Body:
- Excel for Business (8h)
- VBA Mastery (12h)
- Python for Data (16h)
- AI Tools for Business (8h)
```

#### Post 5: Services & Pricing
```
Headline: OUR SERVICES
Body (4 cards):
- FEASIBILITY: 3,000-20,000 DZD
- AUTOMATION: 15,000-75,000 DZD
- TRAINING: 5,000-15,000 DZD
- CONSULTING: Custom Pricing
```

#### Post 6: Contact
```
Headline: GET IN TOUCH
Body:
- Email: kamelmahi71@gmail.com
- Phone: +213 676 77 38 92
- Location: El Bayadh, Algeria
- Web: kamelmahi.netlify.app
```

---

## PART 4: Quick Start (Do This Now)

1. Open https://www.canva.com in browser
2. Sign up / login
3. Click "Brand" → "Brand Kit" → Create "DSC"
4. Upload the two logo files:
   - `C:\Users\Admin\projects\active\digital-services-center\assets\images\logo-hexagon-clean.png`
   - `C:\Users\Admin\projects\active\digital-services-center\images\download.png`
5. Add brand colors (Navy, Gold, White)
6. Create first design: "Instagram Post" (1080x1080)
7. Use template from Part 3 above
8. Download and save to `assets/social/canva/`

---

## File Structure

```
canva-dsc/
├── README.md              (this file)
├── assets/                (upload logos here)
│   ├── logo-hexagon.png
│   └── logo-flat.png
├── templates/             (Canva template links)
└── exports/               (downloaded PNGs)
    ├── profile/
    ├── cover/
    └── posts/
```
