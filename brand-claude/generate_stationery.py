#!/usr/bin/env python3
"""
DSC Stationery Generator
Creates business card, letterhead, and invoice templates.
"""
import os

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BRAND_DIR, "stationery")
os.makedirs(OUT, exist_ok=True)

# Colors
NAVY = "#0A1628"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"
PAPER = "#F5F5F0"
INK = "#1A1A1A"


def mk_svg(scale=1.0, x=0, y=0, color=GOLD, sw=28):
    """MK monogram paths."""
    s = int(sw * scale)
    r = int(14 * scale)
    return f'''<g transform="translate({x}, {y}) scale({scale})">
    <path d="M 80 80 L 80 320 L 140 180 L 200 320 L 200 80"
          fill="none" stroke="{color}" stroke-width="{s}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 200 80 L 200 320" fill="none" stroke="{color}" stroke-width="{s}" stroke-linecap="round"/>
    <path d="M 200 200 L 320 80" fill="none" stroke="{color}" stroke-width="{s}" stroke-linecap="round"/>
    <path d="M 200 200 L 320 320" fill="none" stroke="{color}" stroke-width="{s}" stroke-linecap="round"/>
    <circle cx="200" cy="200" r="{r}" fill="{color}"/>
  </g>'''


def svg_business_card_front():
    """Business card front — MK logo centered on navy."""
    # 90mm x 50mm at 96dpi = 340 x 189px
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 189" width="340" height="189">
  <rect width="100%" height="100%" fill="{NAVY}" rx="8"/>
  {mk_svg(0.35, 110, 10, GOLD)}
  <text x="170" y="170" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="700" fill="{GOLD}" letter-spacing="3">DIGITAL SERVICES CENTER</text>
</svg>'''


def svg_business_card_back():
    """Business card back — contact info."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 189" width="340" height="189">
  <rect width="100%" height="100%" fill="{WHITE}" rx="8"/>
  <!-- Gold accent line -->
  <rect x="0" y="0" width="6" height="189" fill="{GOLD}" rx="3"/>
  <!-- Name -->
  <text x="25" y="40" font-family="Space Grotesk, sans-serif" font-size="16" font-weight="700" fill="{NAVY}">MAHI Kamel Abdelghani</text>
  <text x="25" y="58" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="{GOLD}" letter-spacing="2">DIGITAL SERVICES CENTER</text>
  <!-- Divider -->
  <rect x="25" y="70" width="80" height="1" fill="{GOLD}"/>
  <!-- Contact -->
  <text x="25" y="95" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="{INK}">kamelmahi71@gmail.com</text>
  <text x="25" y="115" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="{INK}">+213 676 77 38 92</text>
  <text x="25" y="135" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="{INK}">El Bayadh, Algeria</text>
  <text x="25" y="155" font-family="Inter, sans-serif" font-size="9" font-weight="400" fill="{INK}">kamelmahi.netlify.app</text>
  <!-- Services -->
  <text x="25" y="178" font-family="Inter, sans-serif" font-size="7" font-weight="400" fill="#999" letter-spacing="1">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</text>
</svg>'''


def svg_letterhead():
    """A4 letterhead template."""
    # A4 at 96dpi = 794 x 1123px
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 794 1123" width="794" height="1123">
  <rect width="100%" height="100%" fill="{WHITE}"/>
  <!-- Header -->
  {mk_svg(0.12, 40, 30, NAVY)}
  <text x="95" y="60" font-family="Space Grotesk, sans-serif" font-size="14" font-weight="700" fill="{NAVY}">Digital Services Center</text>
  <text x="95" y="78" font-family="Inter, sans-serif" font-size="8" font-weight="400" fill="#666" letter-spacing="2">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</text>
  <!-- Header line -->
  <rect x="40" y="95" width="714" height="2" fill="{GOLD}"/>
  <!-- Content area (placeholder lines) -->
  <rect x="40" y="140" width="500" height="1" fill="#ddd"/>
  <rect x="40" y="170" width="600" height="1" fill="#ddd"/>
  <rect x="40" y="200" width="550" height="1" fill="#ddd"/>
  <rect x="40" y="230" width="650" height="1" fill="#ddd"/>
  <rect x="40" y="260" width="400" height="1" fill="#ddd"/>
  <!-- Footer -->
  <rect x="40" y="1060" width="714" height="1" fill="{GOLD}"/>
  <text x="397" y="1085" text-anchor="middle" font-family="Inter, sans-serif" font-size="7" font-weight="400" fill="#999" letter-spacing="2">DIGITAL SERVICES CENTER &bull; El Bayadh, Algeria &bull; kamelmahi71@gmail.com &bull; +213 676 77 38 92</text>
</svg>'''


def svg_invoice():
    """Invoice template."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 794 1123" width="794" height="1123">
  <rect width="100%" height="100%" fill="{WHITE}"/>
  <!-- Header -->
  {mk_svg(0.12, 40, 30, NAVY)}
  <text x="95" y="60" font-family="Space Grotesk, sans-serif" font-size="14" font-weight="700" fill="{NAVY}">Digital Services Center</text>
  <text x="95" y="78" font-family="Inter, sans-serif" font-size="8" font-weight="400" fill="#666" letter-spacing="2">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</text>
  <!-- Header line -->
  <rect x="40" y="95" width="714" height="2" fill="{GOLD}"/>
  <!-- Invoice title -->
  <text x="600" y="140" font-family="Space Grotesk, sans-serif" font-size="32" font-weight="700" fill="{NAVY}">INVOICE</text>
  <!-- Invoice details -->
  <text x="500" y="175" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Invoice #: ___________</text>
  <text x="500" y="195" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Date: ___________</text>
  <text x="500" y="215" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Due: ___________</text>
  <!-- Client info -->
  <text x="40" y="175" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{NAVY}">Bill To:</text>
  <text x="40" y="195" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Client Name: ___________</text>
  <text x="40" y="215" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Address: ___________</text>
  <!-- Table header -->
  <rect x="40" y="260" width="714" height="30" fill="{NAVY}"/>
  <text x="50" y="280" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{WHITE}">DESCRIPTION</text>
  <text x="500" y="280" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{WHITE}">QTY</text>
  <text x="580" y="280" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{WHITE}">PRICE</text>
  <text x="680" y="280" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{WHITE}">TOTAL</text>
  <!-- Table rows -->
  <rect x="40" y="290" width="714" height="30" fill="{PAPER}"/>
  <rect x="40" y="320" width="714" height="30" fill="{WHITE}"/>
  <rect x="40" y="350" width="714" height="30" fill="{PAPER}"/>
  <rect x="40" y="380" width="714" height="30" fill="{WHITE}"/>
  <rect x="40" y="410" width="714" height="30" fill="{PAPER}"/>
  <!-- Total -->
  <rect x="500" y="460" width="254" height="30" fill="{NAVY}"/>
  <text x="510" y="480" font-family="Inter, sans-serif" font-size="12" font-weight="700" fill="{WHITE}">TOTAL: ___________ DZD</text>
  <!-- Payment info -->
  <text x="40" y="530" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="{NAVY}">Payment Terms:</text>
  <text x="40" y="550" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="{INK}">Payment due within 30 days of invoice date.</text>
  <!-- Footer -->
  <rect x="40" y="1060" width="714" height="1" fill="{GOLD}"/>
  <text x="397" y="1085" text-anchor="middle" font-family="Inter, sans-serif" font-size="7" font-weight="400" fill="#999" letter-spacing="2">DIGITAL SERVICES CENTER &bull; El Bayadh, Algeria &bull; kamelmahi71@gmail.com &bull; +213 676 77 38 92</text>
</svg>'''


def svg_letterhead_ar():
    """Arabic letterhead template."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 794 1123" width="794" height="1123">
  <rect width="100%" height="100%" fill="{WHITE}"/>
  <!-- Header -->
  <text x="750" y="60" font-family="Space Grotesk, sans-serif" font-size="14" font-weight="700" fill="{NAVY}" text-anchor="end" direction="rtl">مركز الخدمات الرقمية</text>
  <text x="750" y="78" font-family="Inter, sans-serif" font-size="8" font-weight="400" fill="#666" letter-spacing="2" text-anchor="end" direction="rtl">دراسة جدوى &bull; أتمتة &bull; تدريب</text>
  {mk_svg(0.12, 660, 30, NAVY)}
  <!-- Header line -->
  <rect x="40" y="95" width="714" height="2" fill="{GOLD}"/>
  <!-- Content area -->
  <rect x="150" y="140" width="500" height="1" fill="#ddd"/>
  <rect x="100" y="170" width="600" height="1" fill="#ddd"/>
  <rect x="130" y="200" width="550" height="1" fill="#ddd"/>
  <rect x="80" y="230" width="650" height="1" fill="#ddd"/>
  <rect x="200" y="260" width="400" height="1" fill="#ddd"/>
  <!-- Footer -->
  <rect x="40" y="1060" width="714" height="1" fill="{GOLD}"/>
  <text x="397" y="1085" text-anchor="middle" font-family="Inter, sans-serif" font-size="7" font-weight="400" fill="#999" letter-spacing="2" direction="rtl">مركز الخدمات الرقمية &bull; البаяض، الجزائر &bull; kamelmahi71@gmail.com &bull; +213 676 77 38 92</text>
</svg>'''


# Generate all stationery
if __name__ == "__main__":
    items = {
        "dsc-business-card-front.svg": svg_business_card_front(),
        "dsc-business-card-back.svg": svg_business_card_back(),
        "dsc-letterhead.svg": svg_letterhead(),
        "dsc-letterhead-ar.svg": svg_letterhead_ar(),
        "dsc-invoice.svg": svg_invoice(),
    }
    
    for name, content in items.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK {name}")
    
    print(f"\n{len(items)} stationery SVGs generated in {OUT}")
