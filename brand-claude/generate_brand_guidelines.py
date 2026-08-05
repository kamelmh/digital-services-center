#!/usr/bin/env python3
"""Generate DSC Brand Guidelines PDF from HTML template."""
import os
import base64

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(BRAND_DIR), "assets")

def img_to_base64(path):
    """Convert image to base64 data URI."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.split(".")[-1].lower()
    mime = {"png": "image/png", "svg": "image/svg+xml", "jpg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"

def generate_html():
    """Generate brand guidelines HTML."""
    
    # Load logo images
    logo_navy = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-flat-mk-navy-512.png"))
    logo_white = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-flat-mk-white-512.png"))
    logo_gold = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-flat-mk-gold-512.png"))
    logo_hex = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-hexagon-badge-512.png"))
    logo_lockup = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-horizontal-lockup-1024.png"))
    logo_wordmark = img_to_base64(os.path.join(ASSETS_DIR, "logos", "dsc-wordmark-1024.png"))
    social_profile = img_to_base64(os.path.join(ASSETS_DIR, "social", "profile-400.png"))
    social_cover = img_to_base64(os.path.join(ASSETS_DIR, "social", "cover-1584.png"))
    email_sig = img_to_base64(os.path.join(ASSETS_DIR, "print", "email-signature-400.png"))
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DSC Brand Guidelines v2.0</title>
<style>
@page {{ size: A4; margin: 20mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', 'Segoe UI', sans-serif; color: #1A1A1A; line-height: 1.6; }}
.page {{ page-break-after: always; padding: 40px 0; }}
.page:last-child {{ page-break-after: auto; }}

/* Cover */
.cover {{ display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background: #0A1628; color: white; text-align: center; }}
.cover img {{ width: 200px; margin-bottom: 30px; }}
.cover h1 {{ font-size: 36px; font-weight: 700; letter-spacing: 3px; margin-bottom: 10px; }}
.cover .subtitle {{ font-size: 14px; color: #D4AF37; letter-spacing: 5px; margin-bottom: 40px; }}
.cover .version {{ font-size: 12px; color: #666; letter-spacing: 2px; }}

/* Section headers */
h2 {{ font-size: 24px; font-weight: 700; color: #0A1628; margin: 40px 0 20px; border-bottom: 3px solid #D4AF37; padding-bottom: 10px; letter-spacing: 2px; }}
h3 {{ font-size: 18px; font-weight: 600; color: #0A1628; margin: 30px 0 15px; }}
p {{ margin-bottom: 15px; font-size: 14px; }}

/* Color swatches */
.colors {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 20px 0; }}
.color-swatch {{ width: 120px; text-align: center; }}
.color-swatch .swatch {{ width: 120px; height: 80px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #eee; }}
.color-swatch .name {{ font-weight: 600; font-size: 12px; }}
.color-swatch .hex {{ font-family: monospace; font-size: 11px; color: #666; }}

/* Logo grid */
.logo-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin: 30px 0; }}
.logo-item {{ text-align: center; padding: 20px; background: #f8f8f8; border-radius: 8px; }}
.logo-item img {{ max-width: 150px; max-height: 150px; margin-bottom: 10px; }}
.logo-item.dark {{ background: #0A1628; }}
.logo-item.gold {{ background: #D4AF37; }}
.logo-item .label {{ font-size: 12px; font-weight: 600; color: #333; }}

/* Do/Don't */
.dodont {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 20px 0; }}
.do {{ border: 2px solid #10B981; border-radius: 8px; padding: 20px; }}
.dont {{ border: 2px solid #DC2626; border-radius: 8px; padding: 20px; }}
.do h4 {{ color: #10B981; margin-bottom: 10px; }}
.dont h4 {{ color: #DC2626; margin-bottom: 10px; }}
.do img, .dont img {{ max-width: 100%; margin: 10px 0; }}

/* Typography */
.type-sample {{ margin: 15px 0; padding: 15px; background: #f8f8f8; border-radius: 8px; }}
.type-sample .font-name {{ font-weight: 700; font-size: 16px; margin-bottom: 5px; }}
.type-sample .font-spec {{ font-size: 12px; color: #666; font-family: monospace; }}

/* Spacing */
.spacing-demo {{ background: #f8f8f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}

/* Table */
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }}
th {{ background: #0A1628; color: white; font-weight: 600; }}

/* Footer */
.footer {{ text-align: center; font-size: 11px; color: #999; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
  <img src="{logo_navy}" alt="DSC Logo">
  <h1>DIGITAL SERVICES CENTER</h1>
  <div class="subtitle">FEASIBILITY &bull; AUTOMATION &bull; TRAINING</div>
  <div class="version">BRAND GUIDELINES v2.0</div>
  <div class="version" style="margin-top: 10px;">2026</div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="page">
  <h2>TABLE OF CONTENTS</h2>
  <table>
    <tr><th>#</th><th>Section</th><th>Page</th></tr>
    <tr><td>01</td><td>Brand Overview</td><td>3</td></tr>
    <tr><td>02</td><td>Logo System</td><td>4</td></tr>
    <tr><td>03</td><td>Logo Usage Rules</td><td>5</td></tr>
    <tr><td>04</td><td>Color Palette</td><td>6</td></tr>
    <tr><td>05</td><td>Typography</td><td>7</td></tr>
    <tr><td>06</td><td>Spacing &amp; Clear Zone</td><td>8</td></tr>
    <tr><td>07</td><td>Social Media</td><td>9</td></tr>
    <tr><td>08</td><td>Stationery</td><td>10</td></tr>
    <tr><td>09</td><td>Contact</td><td>11</td></tr>
  </table>
</div>

<!-- BRAND OVERVIEW -->
<div class="page">
  <h2>01. BRAND OVERVIEW</h2>
  <h3>Mission</h3>
  <p>Digital Services Center (DSC) provides feasibility studies, business automation, and professional training for Algerian enterprises and entrepreneurs. We transform ideas into funded businesses.</p>
  
  <h3>Brand DNA</h3>
  <p>The DSC brand is built on three pillars:</p>
  <ul style="margin-left: 20px; margin-bottom: 15px;">
    <li><strong>Precision</strong> &mdash; Data-driven feasibility studies with 95%+ accuracy</li>
    <li><strong>Connection</strong> &mdash; Linking entrepreneurs to funding and success</li>
    <li><strong>Growth</strong> &mdash; Enabling business expansion through technology</li>
  </ul>

  <h3>Brand Values</h3>
  <table>
    <tr><th>Value</th><th>Description</th><th>Visual Expression</th></tr>
    <tr><td>Trust</td><td>Verified, accurate data</td><td>Navy blue, solid typography</td></tr>
    <tr><td>Quality</td><td>Professional deliverables</td><td>Gold accents, clean layout</td></tr>
    <tr><td>Innovation</td><td>Modern solutions</td><td>Interlocking geometry, growth lines</td></tr>
    <tr><td>Accessibility</td><td>Clear communication</td><td>Bilingual text, simple icons</td></tr>
  </table>
</div>

<!-- LOGO SYSTEM -->
<div class="page">
  <h2>02. LOGO SYSTEM</h2>
  <h3>Primary Mark: Interlocking MK Monogram</h3>
  <p>The logo consists of interlocking M and K letters sharing a vertical stroke. The K's upper arm represents the growth line, and the node dot at the joint symbolizes connectivity.</p>
  
  <div class="logo-grid">
    <div class="logo-item dark">
      <img src="{logo_navy}" alt="MK on Navy">
      <div class="label" style="color: white;">Primary (Navy)</div>
    </div>
    <div class="logo-item">
      <img src="{logo_white}" alt="MK on White">
      <div class="label">Reversed (White)</div>
    </div>
    <div class="logo-item gold">
      <img src="{logo_gold}" alt="MK on Gold">
      <div class="label">Gold</div>
    </div>
  </div>

  <h3>Secondary Marks</h3>
  <div class="logo-grid">
    <div class="logo-item">
      <img src="{logo_hex}" alt="Hexagon Badge">
      <div class="label">Hexagon Badge</div>
    </div>
    <div class="logo-item">
      <img src="{logo_lockup}" alt="Horizontal Lockup">
      <div class="label">Horizontal Lockup</div>
    </div>
    <div class="logo-item">
      <img src="{logo_wordmark}" alt="Wordmark">
      <div class="label">Wordmark</div>
    </div>
  </div>
</div>

<!-- LOGO USAGE RULES -->
<div class="page">
  <h2>03. LOGO USAGE RULES</h2>
  
  <div class="dodont">
    <div class="do">
      <h4>DO</h4>
      <ul style="margin-left: 15px;">
        <li>Use approved color combinations</li>
        <li>Maintain minimum clear zone (logo height x 0.5)</li>
        <li>Use SVG for web, PNG for print</li>
        <li>Scale proportionally</li>
        <li>Use on clean backgrounds</li>
      </ul>
    </div>
    <div class="dont">
      <h4>DON'T</h4>
      <ul style="margin-left: 15px;">
        <li>Rotate or skew the logo</li>
        <li>Add shadows or effects</li>
        <li>Change the colors</li>
        <li>Place on busy backgrounds</li>
        <li>Stretch or distort</li>
        <li>Recreate the logo manually</li>
      </ul>
    </div>
  </div>

  <h3>Minimum Sizes</h3>
  <table>
    <tr><th>Application</th><th>Minimum Width</th><th>Format</th></tr>
    <tr><td>Web (screen)</td><td>32px</td><td>SVG</td></tr>
    <tr><td>Social media profile</td><td>170px</td><td>PNG</td></tr>
    <tr><td>Business card</td><td>25mm</td><td>PDF/SVG</td></tr>
    <tr><td>Letterhead</td><td>35mm</td><td>PDF/SVG</td></tr>
    <tr><td>Billboard/banner</td><td>200mm</td><td>PDF/SVG</td></tr>
  </table>
</div>

<!-- COLOR PALETTE -->
<div class="page">
  <h2>04. COLOR PALETTE</h2>
  <h3>Primary Colors</h3>
  <div class="colors">
    <div class="color-swatch">
      <div class="swatch" style="background: #0A1628;"></div>
      <div class="name">Navy</div>
      <div class="hex">#0A1628</div>
      <div class="hex">Pantone 289 C</div>
    </div>
    <div class="color-swatch">
      <div class="swatch" style="background: #D4AF37;"></div>
      <div class="name">Gold</div>
      <div class="hex">#D4AF37</div>
      <div class="hex">Pantone 116 C</div>
    </div>
    <div class="color-swatch">
      <div class="swatch" style="background: #FFFFFF; border: 2px solid #eee;"></div>
      <div class="name">White</div>
      <div class="hex">#FFFFFF</div>
      <div class="hex">CMYK 0/0/0/0</div>
    </div>
  </div>

  <h3>Secondary Colors</h3>
  <div class="colors">
    <div class="color-swatch">
      <div class="swatch" style="background: #F5F5F0;"></div>
      <div class="name">Paper</div>
      <div class="hex">#F5F5F0</div>
    </div>
    <div class="color-swatch">
      <div class="swatch" style="background: #1A1A1A;"></div>
      <div class="name">Ink</div>
      <div class="hex">#1A1A1A</div>
    </div>
    <div class="color-swatch">
      <div class="swatch" style="background: #10B981;"></div>
      <div class="name">Emerald</div>
      <div class="hex">#10B981</div>
    </div>
    <div class="color-swatch">
      <div class="swatch" style="background: #DC2626;"></div>
      <div class="name">Red</div>
      <div class="hex">#DC2626</div>
    </div>
  </div>

  <h3>Color Usage</h3>
  <table>
    <tr><th>Color</th><th>Usage</th><th>Contrast Ratio</th></tr>
    <tr><td>Navy</td><td>Primary backgrounds, headings, logo</td><td>16.2:1 on white</td></tr>
    <tr><td>Gold</td><td>Accents, CTAs, highlights</td><td>3.8:1 on navy</td></tr>
    <tr><td>White</td><td>Reversed text, clean space</td><td>16.2:1 on navy</td></tr>
    <tr><td>Paper</td><td>Document backgrounds</td><td>15.8:1 on ink</td></tr>
    <tr><td>Emerald</td><td>Success states, positive data</td><td>4.5:1 on white</td></tr>
    <tr><td>Red</td><td>Error states, critical alerts</td><td>4.6:1 on white</td></tr>
  </table>
</div>

<!-- TYPOGRAPHY -->
<div class="page">
  <h2>05. TYPOGRAPHY</h2>
  
  <div class="type-sample">
    <div class="font-name" style="font-family: 'Space Grotesk', sans-serif; font-size: 32px;">Space Grotesk</div>
    <div class="font-spec">Display / Headings / Logo text</div>
    <p style="margin-top: 10px; font-family: 'Space Grotesk', sans-serif;">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789</p>
  </div>

  <div class="type-sample">
    <div class="font-name" style="font-family: 'Inter', sans-serif; font-size: 24px;">Inter</div>
    <div class="font-spec">Body text / UI elements</div>
    <p style="margin-top: 10px; font-family: 'Inter', sans-serif;">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789</p>
  </div>

  <div class="type-sample">
    <div class="font-name" style="font-family: 'JetBrains Mono', monospace; font-size: 20px;">JetBrains Mono</div>
    <div class="font-spec">Code / Data / Technical specs</div>
    <p style="margin-top: 10px; font-family: 'JetBrains Mono', monospace;">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789</p>
  </div>

  <h3>Type Scale</h3>
  <table>
    <tr><th>Level</th><th>Font</th><th>Size</th><th>Weight</th></tr>
    <tr><td>H1</td><td>Space Grotesk</td><td>36px</td><td>700</td></tr>
    <tr><td>H2</td><td>Space Grotesk</td><td>28px</td><td>700</td></tr>
    <tr><td>H3</td><td>Space Grotesk</td><td>22px</td><td>600</td></tr>
    <tr><td>Body</td><td>Inter</td><td>16px</td><td>400</td></tr>
    <tr><td>Small</td><td>Inter</td><td>14px</td><td>400</td></tr>
    <tr><td>Caption</td><td>Inter</td><td>12px</td><td>400</td></tr>
    <tr><td>Code</td><td>JetBrains Mono</td><td>14px</td><td>400</td></tr>
  </table>
</div>

<!-- SPACING & CLEAR ZONE -->
<div class="page">
  <h2>06. SPACING &amp; CLEAR ZONE</h2>
  <h3>Logo Clear Zone</h3>
  <p>The minimum clear zone around the logo must be equal to the height of the "M" letterform. This ensures the logo maintains its visual impact and readability.</p>
  
  <div class="spacing-demo">
    <p><strong>Minimum clear zone:</strong> Logo height &times; 0.5 on all sides</p>
    <p><strong>Spacing unit:</strong> Based on the node dot diameter (14px at 100%)</p>
    <p><strong>Grid:</strong> 8px base grid for all layouts</p>
  </div>

  <h3>Layout Grid</h3>
  <table>
    <tr><th>Element</th><th>Spacing</th><th>Notes</th></tr>
    <tr><td>Page margins</td><td>20mm (print), 16px (web)</td><td>Consistent across all formats</td></tr>
    <tr><td>Section spacing</td><td>40px</td><td>Between major sections</td></tr>
    <tr><td>Element spacing</td><td>16px</td><td>Between related elements</td></tr>
    <tr><td>Line height</td><td>1.6</td><td>For body text</td></tr>
  </table>
</div>

<!-- SOCIAL MEDIA -->
<div class="page">
  <h2>07. SOCIAL MEDIA</h2>
  <h3>Profile Image</h3>
  <div style="text-align: center; margin: 20px 0;">
    <img src="{social_profile}" alt="Profile" style="width: 200px; border-radius: 50%;">
    <p style="margin-top: 10px; font-size: 12px; color: #666;">Facebook / LinkedIn / Twitter<br>400 &times; 400px</p>
  </div>

  <h3>Cover Image</h3>
  <div style="text-align: center; margin: 20px 0;">
    <img src="{social_cover}" alt="Cover" style="width: 100%; max-width: 600px;">
    <p style="margin-top: 10px; font-size: 12px; color: #666;">Facebook / LinkedIn Cover<br>1584 &times; 396px</p>
  </div>
</div>

<!-- STATIONERY -->
<div class="page">
  <h2>08. STATIONERY</h2>
  <h3>Email Signature</h3>
  <div style="text-align: center; margin: 20px 0;">
    <img src="{email_sig}" alt="Email Signature" style="width: 400px;">
    <p style="margin-top: 10px; font-size: 12px; color: #666;">Email signature<br>400 &times; 100px</p>
  </div>

  <h3>Business Card</h3>
  <table>
    <tr><th>Side</th><th>Content</th><th>Specs</th></tr>
    <tr><td>Front</td><td>MK logo + company name</td><td>90 &times; 50mm, 300dpi</td></tr>
    <tr><td>Back</td><td>Contact info + services</td><td>90 &times; 50mm, 300dpi</td></tr>
  </table>

  <h3>Letterhead</h3>
  <table>
    <tr><th>Element</th><th>Position</th><th>Size</th></tr>
    <tr><td>Logo</td><td>Top-left</td><td>35mm wide</td></tr>
    <tr><td>Company info</td><td>Top-right</td><td>10pt Inter</td></tr>
    <tr><td>Footer</td><td>Bottom center</td><td>8pt Inter, gold</td></tr>
  </table>
</div>

<!-- CONTACT -->
<div class="page">
  <h2>09. CONTACT</h2>
  <h3>Digital Services Center</h3>
  <p><strong>Developer:</strong> MAHI Kamel Abdelghani</p>
  <p><strong>Email:</strong> kamelmahi71@gmail.com</p>
  <p><strong>Phone:</strong> +213 676 77 38 92</p>
  <p><strong>Location:</strong> El Bayadh, Algeria</p>
  <p><strong>Portfolio:</strong> https://kamelmahi.netlify.app</p>
  <p><strong>GitHub:</strong> https://github.com/kamelmh/digital-services-center</p>
  
  <div class="footer">
    <p>Digital Services Center &copy; 2026. All rights reserved.</p>
    <p>Brand Guidelines v2.0 &mdash; Confidential</p>
  </div>
</div>

</body>
</html>'''
    return html


if __name__ == "__main__":
    html = generate_html()
    out_path = os.path.join(BRAND_DIR, "DSC_Brand_Guidelines_v2.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML generated: {out_path}")
    print("Open in browser and print to PDF (Ctrl+P -> Save as PDF)")
