# Digital Services Center — Templates

## Overview

This folder contains HTML templates for all Digital Services Center marketing and business materials. Each template is designed to be opened in a browser and printed to PDF or exported as an image.

## Templates

| Template | File | Size | Purpose |
|----------|------|------|---------|
| **Business Card** | `business-card.html` | 3.5 x 2 in | Front & back business cards |
| **Letterhead** | `letterhead.html` | A4 | Official letter template |
| **Invoice** | `invoice.html` | A4 | Client invoice |
| **Social Media** | `social-media.html` | 1080x1080, 1200x630 | Instagram, Facebook, LinkedIn posts |
| **Service Menu** | `service-menu.html` | A4 | Printable service catalog |

## How to Use

### 1. Open in Browser
Double-click any `.html` file to open it in your default browser.

### 2. Export to PDF
1. Press `Ctrl + P` (or `Cmd + P` on Mac)
2. Select "Save as PDF" as the destination
3. Click "Save"

### 3. Export to Image
1. Open the HTML file in Chrome/Edge
2. Press `F12` to open DevTools
3. Press `Ctrl + Shift + P` to open Command Menu
4. Type "screenshot" and select "Capture full size screenshot"
5. Save the image

## Customization

### Change Colors
Edit the CSS variables in each file:
```css
:root {
    --navy: #0A1628;
    --gold: #D4AF37;
    --white: #FFFFFF;
}
```

### Change Content
Edit the HTML content directly. Look for placeholder text like:
- `[DATE]`
- `[NOM DU CLIENT]`
- `[DESCRIPTION DU SERVICE]`
- `[PRIX] DZD`

### Change Logo
Replace the logo div with an `<img>` tag:
```html
<div class="logo">
    <img src="../assets/images/logo-hexagon-clean.png" alt="MK Logo">
</div>
```

## File Naming

When exporting, use this naming convention:
```
dsc-[type]-[variant]-[size].[ext]
```

### Examples
- `dsc-businesscard-front-300dpi.pdf`
- `dsc-letterhead-a4.pdf`
- `dsc-invoice-001.pdf`
- `dsc-social-instagram-1080x1080.png`
- `dsc-servicemenu-a4-print.pdf`

## Design System

For complete design guidelines, see `DESIGN_SYSTEM.md` in the project root.

## Next Steps

1. **Print business cards** — Export `business-card.html` to PDF, print at local print shop
2. **Print letterheads** — Export `letterhead.html` to PDF, print 100 copies
3. **Create invoices** — Use `invoice.html` for client billing
4. **Schedule social posts** — Export images, schedule with Meta Business Suite
5. **Print service menus** — Export `service-menu.html`, distribute to businesses
