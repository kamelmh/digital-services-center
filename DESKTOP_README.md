# DSC Desktop App

## What is this?

A standalone desktop application for generating professional Arabic/French bilingual documents for Algerian businesses. Run it on any Windows PC — no internet required, no server costs, no monthly fees.

## Features

- **Feasibility Studies** — 9-section Arabic/French bilingual
- **NESDA Dossiers** — 9-part financing applications
- **Tax Forms** — G1, G4, G8, G11, G12, G29, G50
- **Business Plans** — Full business plans
- **BMC** — Business Model Canvas
- **Financial Projections** — 5-year VAN/TRI
- **CV + Cover Letters** — Professional PDFs
- **Invoices** — Generate invoices for clients
- **Calculators** — VAN, TRI, break-even
- **NESDA Calculator** — Financing breakdown
- **NESDA Catalog** — 51 eligible activities
- **Batch Processing** — Multiple clients at once

## How to use

### Option 1: Run from source (recommended for development)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python desktop_app.py

# Open http://localhost:8501 in your browser
```

### Option 2: Build .exe (for distribution)
```bash
# Run the build script
build_desktop.bat

# Output: dist/DSC_Digital_Services_Center.exe
```

### Option 3: Use pre-built .exe
1. Download `DSC_Digital_Services_Center.exe`
2. Double-click to run
3. Open http://localhost:8501 in your browser

## System requirements

- Windows 10/11
- 4 GB RAM
- 500 MB disk space
- No internet required (offline mode)

## Distribution

### Via USB drive
1. Copy .exe to USB drive
2. Give to client
3. They double-click to run

### Via WhatsApp/Email
1. Compress .exe to ZIP (~30 MB)
2. Send via WhatsApp/Email
3. Client extracts and runs

### Via Google Drive
1. Upload .exe to Google Drive
2. Share link with client
3. Client downloads and runs

## Troubleshooting

### "Python not found"
- Install Python 3.12 from https://python.org
- Check "Add Python to PATH" during installation

### "Module not found"
- Run: `pip install -r requirements.txt`

### "Port 8501 already in use"
- Close other instances of the app
- Or change port in `main.py`

### "Antivirus blocking"
- Some antivirus software flags PyInstaller executables
- Add exception or disable temporarily

## Support

- WhatsApp: +213 676 773 892
- Email: contact@dsc-dz.com
- GitHub: https://github.com/kamelmh/digital-services-center

## License

Proprietary — All rights reserved.
