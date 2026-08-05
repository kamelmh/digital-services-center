#!/usr/bin/env python3
"""
DSC Social Media Kit Generator
Creates 7 professional social media images with correct branding.
"""
import os
import math

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BRAND_DIR, "social-kit")
os.makedirs(OUT, exist_ok=True)

# Colors
NAVY = "#0A1628"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"
PAPER = "#F5F5F0"
EMERALD = "#10B981"
RED = "#DC2626"


def mk_svg_content(scale=1.0, x=0, y=0, color=GOLD, stroke_width=28):
    """MK monogram SVG paths."""
    sw = int(stroke_width * scale)
    r = int(14 * scale)
    return f'''<g transform="translate({x}, {y}) scale({scale})">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320"
          fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80"
          fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320"
          fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="{r}" fill="{color}"/>
  </g>'''


def svg_profile():
    """Facebook/LinkedIn profile picture."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  {mk_svg_content(0.7, 90, 40, GOLD)}
</svg>'''


def svg_cover():
    """Facebook/LinkedIn cover photo."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1584 396" width="1584" height="396">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- Subtle pattern -->
  <defs>
    <pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="1" fill="{GOLD}" opacity="0.1"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#dots)"/>
  <!-- MK icon left -->
  {mk_svg_content(0.5, 80, 20, GOLD)}
  <!-- Company name -->
  <text x="320" y="180" font-family="Space Grotesk, sans-serif" font-size="56" font-weight="700" fill="{WHITE}" letter-spacing="3">DIGITAL SERVICES CENTER</text>
  <!-- Tagline -->
  <text x="320" y="230" font-family="Inter, sans-serif" font-size="20" font-weight="400" fill="{GOLD}" letter-spacing="6">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</text>
  <!-- Contact -->
  <text x="320" y="280" font-family="Inter, sans-serif" font-size="14" font-weight="400" fill="#666" letter-spacing="2">kamelmahi71@gmail.com | +213 676 77 38 92</text>
  <!-- Gold accent line -->
  <rect x="320" y="250" width="200" height="2" fill="{GOLD}"/>
</svg>'''


def svg_post_feasibility():
    """Feasibility Studies post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- Decorative elements -->
  <rect x="0" y="0" width="8" height="1080" fill="{GOLD}"/>
  <circle cx="900" cy="180" r="200" fill="{GOLD}" opacity="0.05"/>
  <circle cx="950" cy="230" r="150" fill="{GOLD}" opacity="0.08"/>
  <!-- MK icon top-right -->
  {mk_svg_content(0.2, 920, 30, GOLD)}
  <!-- Content -->
  <text x="80" y="350" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">FEASIBILITY</text>
  <text x="80" y="430" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">STUDIES</text>
  <!-- Gold accent line -->
  <rect x="80" y="460" width="160" height="4" fill="{GOLD}"/>
  <!-- Subtitle -->
  <text x="80" y="520" font-family="Inter, sans-serif" font-size="24" font-weight="400" fill="{GOLD}">From Idea to Funded Business</text>
  <!-- Features -->
  <text x="80" y="600" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Diagnostic Express ........... 3,000 DZD</text>
  <text x="80" y="640" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Pre-Feasibility .............. 8,000 DZD</text>
  <text x="80" y="680" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Complete Study ........... 15,000 DZD</text>
  <text x="80" y="720" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Bank Dossier ............. 12,000 DZD</text>
  <!-- Bottom bar -->
  <rect x="0" y="1000" width="1080" height="80" fill="{GOLD}"/>
  <text x="540" y="1048" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="18" font-weight="700" fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''


def svg_post_automation():
    """Business Automation post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- Decorative -->
  <rect x="0" y="0" width="8" height="1080" fill="{EMERALD}"/>
  <circle cx="900" cy="180" r="200" fill="{EMERALD}" opacity="0.05"/>
  <!-- MK icon top-right -->
  {mk_svg_content(0.2, 920, 30, GOLD)}
  <!-- Content -->
  <text x="80" y="350" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">BUSINESS</text>
  <text x="80" y="430" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">AUTOMATION</text>
  <!-- Gold accent -->
  <rect x="80" y="460" width="160" height="4" fill="{GOLD}"/>
  <!-- Subtitle -->
  <text x="80" y="520" font-family="Inter, sans-serif" font-size="24" font-weight="400" fill="{EMERALD}">Excel &bull; VBA &bull; Python &bull; AI</text>
  <!-- Tools -->
  <text x="80" y="600" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" VBA Macros &amp; Automation</text>
  <text x="80" y="640" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Python Data Pipelines</text>
  <text x="80" y="680" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" AI-Powered Dashboards</text>
  <text x="80" y="720" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Inventory Management Systems</text>
  <!-- Bottom bar -->
  <rect x="0" y="1000" width="1080" height="80" fill="{GOLD}"/>
  <text x="540" y="1048" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="18" font-weight="700" fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''


def svg_post_training():
    """Professional Training post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- Decorative -->
  <rect x="0" y="0" width="8" height="1080" fill="{GOLD}"/>
  <circle cx="900" cy="180" r="200" fill="{GOLD}" opacity="0.05"/>
  <!-- MK icon top-right -->
  {mk_svg_content(0.2, 920, 30, GOLD)}
  <!-- Content -->
  <text x="80" y="350" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">PROFESSIONAL</text>
  <text x="80" y="430" font-family="Space Grotesk, sans-serif" font-size="64" font-weight="700" fill="{WHITE}">TRAINING</text>
  <!-- Gold accent -->
  <rect x="80" y="460" width="160" height="4" fill="{GOLD}"/>
  <!-- Subtitle -->
  <text x="80" y="520" font-family="Inter, sans-serif" font-size="24" font-weight="400" fill="{GOLD}">Skills That Pay The Bills</text>
  <!-- Courses -->
  <text x="80" y="600" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Excel for Business (8h)</text>
  <text x="80" y="640" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" VBA Mastery (12h)</text>
  <text x="80" y="680" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" Python for Data (16h)</text>
  <text x="80" y="720" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">" AI Tools for Business (8h)</text>
  <!-- Bottom bar -->
  <rect x="0" y="1000" width="1080" height="80" fill="{GOLD}"/>
  <text x="540" y="1048" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="18" font-weight="700" fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''


def svg_post_about():
    """About Us post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- MK icon centered -->
  {mk_svg_content(0.6, 420, 80, GOLD)}
  <!-- Company name -->
  <text x="540" y="450" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="48" font-weight="700" fill="{WHITE}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
  <!-- Gold accent -->
  <rect x="390" y="480" width="300" height="3" fill="{GOLD}"/>
  <!-- Tagline -->
  <text x="540" y="530" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="400" fill="{GOLD}" letter-spacing="5">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</text>
  <!-- Services -->
  <text x="540" y="620" text-anchor="middle" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">Feasibility Studies &amp; Business Plans</text>
  <text x="540" y="660" text-anchor="middle" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">Business Automation &amp; AI Solutions</text>
  <text x="540" y="700" text-anchor="middle" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{WHITE}">Professional Training &amp; Consulting</text>
  <!-- Contact -->
  <text x="540" y="800" text-anchor="middle" font-family="Inter, sans-serif" font-size="14" font-weight="400" fill="#666">kamelmahi71@gmail.com | +213 676 77 38 92</text>
  <text x="540" y="830" text-anchor="middle" font-family="Inter, sans-serif" font-size="14" font-weight="400" fill="#666">El Bayadh, Algeria</text>
</svg>'''


def svg_post_contact():
    """Contact Us post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- MK icon top-left -->
  {mk_svg_content(0.15, 60, 60, GOLD)}
  <!-- Content -->
  <text x="540" y="350" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="72" font-weight="700" fill="{WHITE}">GET IN TOUCH</text>
  <!-- Gold accent -->
  <rect x="390" y="390" width="300" height="4" fill="{GOLD}"/>
  <!-- Contact info -->
  <text x="540" y="500" text-anchor="middle" font-family="Inter, sans-serif" font-size="24" font-weight="500" fill="{GOLD}">Email</text>
  <text x="540" y="540" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="400" fill="{WHITE}">kamelmahi71@gmail.com</text>
  <text x="540" y="620" text-anchor="middle" font-family="Inter, sans-serif" font-size="24" font-weight="500" fill="{GOLD}">Phone / WhatsApp</text>
  <text x="540" y="660" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="400" fill="{WHITE}">+213 676 77 38 92</text>
  <text x="540" y="740" text-anchor="middle" font-family="Inter, sans-serif" font-size="24" font-weight="500" fill="{GOLD}">Location</text>
  <text x="540" y="780" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="400" fill="{WHITE}">El Bayadh, Algeria</text>
  <!-- Bottom bar -->
  <rect x="0" y="1000" width="1080" height="80" fill="{GOLD}"/>
  <text x="540" y="1048" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="18" font-weight="700" fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''


def svg_post_pricing():
    """Services & Pricing post."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <rect width="100%" height="100%" fill="{NAVY}"/>
  <!-- Decorative -->
  <rect x="0" y="0" width="8" height="1080" fill="{GOLD}"/>
  <!-- MK icon top-right -->
  {mk_svg_content(0.2, 920, 30, GOLD)}
  <!-- Content -->
  <text x="80" y="200" font-family="Space Grotesk, sans-serif" font-size="56" font-weight="700" fill="{WHITE}">OUR SERVICES</text>
  <rect x="80" y="230" width="120" height="3" fill="{GOLD}"/>
  <!-- Service cards -->
  <rect x="80" y="280" width="440" height="180" rx="8" fill="{GOLD}" opacity="0.1"/>
  <text x="100" y="330" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{GOLD}">FEASIBILITY</text>
  <text x="100" y="370" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">Diagnostic, Pre-Feasibility,</text>
  <text x="100" y="395" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">Complete Study, Bank Dossier</text>
  <text x="100" y="435" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="{GOLD}">3,000 - 20,000 DZD</text>
  
  <rect x="560" y="280" width="440" height="180" rx="8" fill="{GOLD}" opacity="0.1"/>
  <text x="580" y="330" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{GOLD}">AUTOMATION</text>
  <text x="580" y="370" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">VBA Macros, Python Scripts,</text>
  <text x="580" y="395" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">AI Dashboards, SIS</text>
  <text x="580" y="435" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="{GOLD}">15,000 - 75,000 DZD</text>
  
  <rect x="80" y="500" width="440" height="180" rx="8" fill="{GOLD}" opacity="0.1"/>
  <text x="100" y="550" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{GOLD}">TRAINING</text>
  <text x="100" y="590" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">Excel, VBA, Python,</text>
  <text x="100" y="615" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">AI Tools for Business</text>
  <text x="100" y="655" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="{GOLD}">5,000 - 15,000 DZD</text>
  
  <rect x="560" y="500" width="440" height="180" rx="8" fill="{GOLD}" opacity="0.1"/>
  <text x="580" y="550" font-family="Space Grotesk, sans-serif" font-size="28" font-weight="700" fill="{GOLD}">CONSULTING</text>
  <text x="580" y="590" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">Strategy, Digital Transformation,</text>
  <text x="580" y="615" font-family="Inter, sans-serif" font-size="16" font-weight="400" fill="{WHITE}">Business Process Optimization</text>
  <text x="580" y="655" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="{GOLD}">Custom Pricing</text>
  
  <!-- Bottom bar -->
  <rect x="0" y="1000" width="1080" height="80" fill="{GOLD}"/>
  <text x="540" y="1048" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="18" font-weight="700" fill="{NAVY}" letter-spacing="4">DIGITAL SERVICES CENTER</text>
</svg>'''


# Generate all social media SVGs
if __name__ == "__main__":
    posts = {
        "dsc-social-profile.svg": svg_profile(),
        "dsc-social-cover.svg": svg_cover(),
        "dsc-social-post-feasibility.svg": svg_post_feasibility(),
        "dsc-social-post-automation.svg": svg_post_automation(),
        "dsc-social-post-training.svg": svg_post_training(),
        "dsc-social-post-about.svg": svg_post_about(),
        "dsc-social-post-contact.svg": svg_post_contact(),
        "dsc-social-post-pricing.svg": svg_post_pricing(),
    }
    
    for name, content in posts.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK {name}")
    
    print(f"\n{len(posts)} social media SVGs generated in {OUT}")
