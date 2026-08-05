#!/usr/bin/env python3
"""
DSC Interlocking MK Logo Generator
Creates the correct interlocking MK monogram SVGs.

Design DNA:
- M and K share a vertical stroke
- K's upper arm = growth line
- Node dot at joint = connectivity
- Flat vector, no effects
- Navy #0A1628, Gold #D4AF37
"""
import os
import math

# Colors
NAVY = "#0A1628"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"
PAPER = "#F5F5F0"
EMERALD = "#10B981"

# Output directory
OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)


def svg_flat_mk(width=400, height=400, bg=None):
    """Flat interlocking MK monogram — no frame."""
    # The M: left vertical, left diagonal, right diagonal, right vertical (shared with K)
    # The K: shared vertical, upper arm (growth line), lower arm
    # Node dot at the joint point

    # Key coordinates (in 400x400 space, centered)
    # Shared vertical: x=140, y=80 to y=320
    # M left vertical: x=80, y=80 to y=320
    # M diagonals: (80,80)→(140,180) and (140,180)→(200,80)
    # K upper arm (growth line): (140,200)→(280,80) — this is the growth line
    # K lower arm: (140,200)→(280,320)
    # Node dot at joint: circle at (140,200) r=12

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {"<rect width=\"100%\" height=\"100%\" fill=\"" + bg + "\"/>" if bg else ""}
  <g transform="translate(60, 40) scale(0.8)">
    <!-- M letter -->
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- K letter — shares vertical with M -->
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <!-- K upper arm (growth line) -->
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <!-- K lower arm -->
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <!-- Node dot at joint — connectivity -->
    <circle cx="200" cy="200" r="14" fill="{GOLD}"/>
  </g>
</svg>'''
    return svg


def svg_flat_mk_navy(width=400, height=400):
    """Flat MK on navy background — the core logo."""
    return svg_flat_mk(width, height, bg=NAVY)


def svg_flat_mk_white(width=400, height=400):
    """Flat MK on white background."""
    return svg_flat_mk(width, height, bg=WHITE)


def svg_flat_mk_gold(width=400, height=400):
    """Flat MK on gold background — inverted."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="{GOLD}"/>
  <g transform="translate(60, 40) scale(0.8)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{NAVY}"/>
  </g>
</svg>'''
    return svg


def svg_flat_mk_transparent(width=400, height=400):
    """Flat MK on transparent background — for overlays."""
    return svg_flat_mk(width, height, bg=None)


def svg_hexagon_badge(width=400, height=440):
    """MK inside hexagon badge — the shield version."""
    # Hexagon points (center 200,220, radius 180)
    cx, cy, r = 200, 220, 180
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 90)
        points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
    hex_points = " ".join(points)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <!-- Navy hexagon -->
  <polygon points="{hex_points}" fill="{NAVY}" stroke="{GOLD}" stroke-width="3"/>
  <!-- MK monogram inside -->
  <g transform="translate(68, 58) scale(0.8)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{GOLD}"/>
  </g>
  <!-- "DIGITAL SERVICES CENTER" text arc below hexagon -->
  <text x="{cx}" y="{cy + r + 30}" text-anchor="middle"
        font-family="Space Grotesk, sans-serif" font-size="14" font-weight="700"
        fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''
    return svg


def svg_horizontal_lockup(width=600, height=150):
    """MK icon + full name horizontal lockup."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <!-- MK icon (left) -->
  <g transform="translate(15, 15) scale(0.3)">
    <rect width="400" height="400" rx="20" fill="{NAVY}"/>
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{GOLD}"/>
  </g>
  <!-- Text (right) -->
  <text x="150" y="75" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{NAVY}">Digital Services</text>
  <text x="150" y="110" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{NAVY}">Center</text>
  <text x="150" y="135" font-family="Inter, sans-serif" font-size="12" font-weight="400" fill="#666" letter-spacing="3">FEASIBILITY • AUTOMATION • TRAINING</text>
</svg>'''
    return svg


def svg_wordmark(width=600, height=100):
    """Text-only wordmark — no icon."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <text x="300" y="55" text-anchor="middle"
        font-family="Space Grotesk, sans-serif" font-size="36" font-weight="700"
        fill="{NAVY}" letter-spacing="2">DIGITAL SERVICES CENTER</text>
  <text x="300" y="80" text-anchor="middle"
        font-family="Inter, sans-serif" font-size="12" font-weight="400"
        fill="#666" letter-spacing="5">FEASIBILITY STUDIES • BUSINESS AUTOMATION • TRAINING</text>
</svg>'''
    return svg


def svg_social_profile(width=400, height=400):
    """Facebook/LinkedIn profile — MK centered on navy."""
    return svg_flat_mk_navy(400, 400)


def svg_social_cover(width=1584, height=396):
    """Facebook cover — horizontal lockup centered."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- MK icon centered -->
  <g transform="translate({width//2 - 100}, 50) scale(0.5)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{GOLD}"/>
  </g>
  <!-- Company name -->
  <text x="{width//2}" y="280" text-anchor="middle"
        font-family="Space Grotesk, sans-serif" font-size="32" font-weight="700"
        fill="{WHITE}" letter-spacing="3">DIGITAL SERVICES CENTER</text>
  <!-- Tagline -->
  <text x="{width//2}" y="320" text-anchor="middle"
        font-family="Inter, sans-serif" font-size="14" font-weight="400"
        fill="{GOLD}" letter-spacing="5">FEASIBILITY • AUTOMATION • TRAINING</text>
</svg>'''
    return svg


def svg_social_post(title="Feasibility Studies", subtitle="From Idea to Funded Business", width=1080, height=1080):
    """Social media post template — logo + headline."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- MK icon top-right -->
  <g transform="translate({width-160}, 40) scale(0.25)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{GOLD}"/>
  </g>
  <!-- Gold accent line -->
  <rect x="80" y="380" width="120" height="4" fill="{GOLD}"/>
  <!-- Title -->
  <text x="80" y="450" font-family="Space Grotesk, sans-serif" font-size="48" font-weight="700" fill="{WHITE}">{title}</text>
  <!-- Subtitle -->
  <text x="80" y="510" font-family="Inter, sans-serif" font-size="22" font-weight="400" fill="{GOLD}">{subtitle}</text>
  <!-- Bottom bar -->
  <rect x="0" y="{height-80}" width="{width}" height="80" fill="{GOLD}"/>
  <text x="{width//2}" y="{height-35}" text-anchor="middle"
        font-family="Space Grotesk, sans-serif" font-size="16" font-weight="700"
        fill="{NAVY}" letter-spacing="3">DIGITAL SERVICES CENTER</text>
</svg>'''
    return svg


def svg_favicon(size=32):
    """Small favicon — just MK marks."""
    s = size
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}">
  <rect width="100%" height="100%" rx="4" fill="{NAVY}"/>
  <g transform="translate({s*0.15}, {s*0.1}) scale({s/500})">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{GOLD}" stroke-width="35" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{GOLD}" stroke-width="35" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{GOLD}" stroke-width="35" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{GOLD}" stroke-width="35" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="18" fill="{GOLD}"/>
  </g>
</svg>'''
    return svg


def svg_email_signature(width=400, height=100):
    """Email signature — horizontal lockup."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect x="0" y="0" width="4" height="{height}" fill="{GOLD}"/>
  <!-- MK icon -->
  <g transform="translate(15, 10) scale(0.2)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{NAVY}"/>
  </g>
  <!-- Text -->
  <text x="65" y="40" font-family="Space Grotesk, sans-serif" font-size="14" font-weight="700" fill="{NAVY}">Digital Services Center</text>
  <text x="65" y="60" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="#666">MAHI Kamel Abdelghani</text>
  <text x="65" y="78" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="#666">kamelmahi71@gmail.com | +213 676 77 38 92</text>
</svg>'''
    return svg


def svg_watermark(width=200, height=60):
    """Footer watermark for documents."""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <g transform="translate(5, 5) scale(0.12)">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{NAVY}" stroke-width="28" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="14" fill="{NAVY}"/>
  </g>
  <text x="55" y="38" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="700" fill="{NAVY}">DSC</text>
</svg>'''
    return svg


# ──────────────────────────────────────────────
# GENERATE ALL LOGOS
# ──────────────────────────────────────────────
if __name__ == "__main__":
    logos = {
        "dsc-flat-mk-navy.svg": svg_flat_mk_navy(),
        "dsc-flat-mk-white.svg": svg_flat_mk_white(),
        "dsc-flat-mk-gold.svg": svg_flat_mk_gold(),
        "dsc-flat-mk-transparent.svg": svg_flat_mk_transparent(),
        "dsc-hexagon-badge.svg": svg_hexagon_badge(),
        "dsc-horizontal-lockup.svg": svg_horizontal_lockup(),
        "dsc-wordmark.svg": svg_wordmark(),
        "dsc-social-profile.svg": svg_social_profile(),
        "dsc-social-cover.svg": svg_social_cover(),
        "dsc-social-post-feasibility.svg": svg_social_post("Feasibility Studies", "From Idea to Funded Business"),
        "dsc-social-post-automation.svg": svg_social_post("Business Automation", "Excel • VBA • Python • AI"),
        "dsc-social-post-training.svg": svg_social_post("Professional Training", "Skills That Pay The Bills"),
        "dsc-favicon-32.svg": svg_favicon(32),
        "dsc-favicon-16.svg": svg_favicon(16),
        "dsc-email-signature.svg": svg_email_signature(),
        "dsc-watermark.svg": svg_watermark(),
    }

    for name, content in logos.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK {name}")

    print(f"\n{len(logos)} SVG logos generated in {OUT}")
