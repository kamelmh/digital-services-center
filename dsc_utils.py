"""
DSC Shared Utilities — UX, PDF export, Arabic fonts, database.
All pages import from here for enhanced functionality.
"""
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

# ── Arabic Font CSS ──────────────────────────────────────────────────────────

ARABIC_FONT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

:root {
    --font-ar: 'Noto Sans Arabic', 'Tahoma', 'Arial', sans-serif;
    --font-ar-serif: 'Amiri', 'Traditional Arabic', serif;
}

[dir="rtl"], .rtl, [lang="ar"] {
    font-family: var(--font-ar);
    direction: rtl;
    text-align: right;
}

/* Arabic content blocks */
.ar-text {
    font-family: var(--font-ar);
    direction: rtl;
    text-align: right;
    line-height: 1.8;
    font-size: 1.05em;
}

.ar-serif {
    font-family: var(--font-ar-serif);
    direction: rtl;
    text-align: right;
    line-height: 2;
}

/* Bilingual layout */
.bilingual {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    direction: ltr;
}

.bilingual .ar-side {
    direction: rtl;
    text-align: right;
    font-family: var(--font-ar);
    border-right: 3px solid #0A1628;
    padding-right: 15px;
}

.bilingual .fr-side {
    direction: ltr;
    text-align: left;
    border-left: 3px solid #ddd;
    padding-left: 15px;
}
</style>
"""

# ── Loading & Progress UX ────────────────────────────────────────────────────

def loading_spinner(message: str = "Processing..."):
    """Show a loading spinner with message."""
    return f"""
    <div style="display:flex;align-items:center;gap:10px;padding:15px;background:#f0f7ff;border-radius:8px;border-left:4px solid #2196F3;">
        <div style="width:20px;height:20px;border:3px solid #ddd;border-top:3px solid #2196F3;border-radius:50%;animation:spin 1s linear infinite;"></div>
        <strong>{message}</strong>
    </div>
    <style>@keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style>
    """


def progress_bar(current: int, total: int, label: str = ""):
    """Show a progress bar."""
    pct = int(current / total * 100) if total > 0 else 0
    return f"""
    <div style="margin:8px 0;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-weight:500;">{label}</span>
            <span style="color:#666;">{current}/{total} ({pct}%)</span>
        </div>
        <div style="background:#e0e0e0;border-radius:10px;height:8px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#2196F3,#4CAF50);height:100%;width:{pct}%;transition:width 0.3s;border-radius:10px;"></div>
        </div>
    </div>
    """


def success_box(title: str, message: str):
    """Show a success message box."""
    return f"""
    <div style="background:#e8f5e9;padding:15px;border-radius:8px;border-left:4px solid #4CAF50;margin:10px 0;">
        <strong style="color:#2e7d32;">✓ {title}</strong>
        <p style="margin:5px 0 0;color:#333;">{message}</p>
    </div>
    """


def error_box(title: str, message: str):
    """Show an error message box."""
    return f"""
    <div style="background:#ffebee;padding:15px;border-radius:8px;border-left:4px solid #f44336;margin:10px 0;">
        <strong style="color:#c62828;">✗ {title}</strong>
        <p style="margin:5px 0 0;color:#333;">{message}</p>
    </div>
    """


def warning_box(title: str, message: str):
    """Show a warning message box."""
    return f"""
    <div style="background:#fff3e0;padding:15px;border-radius:8px;border-left:4px solid #ff9800;margin:10px 0;">
        <strong style="color:#e65100;">⚠ {title}</strong>
        <p style="margin:5px 0 0;color:#333;">{message}</p>
    </div>
    """


def info_box(title: str, message: str):
    """Show an info message box."""
    return f"""
    <div style="background:#e3f2fd;padding:15px;border-radius:8px;border-left:4px solid #2196F3;margin:10px 0;">
        <strong style="color:#1565c0;">ℹ {title}</strong>
        <p style="margin:5px 0 0;color:#333;">{message}</p>
    </div>
    """


def stat_card(label: str, value: str, icon: str = "", color: str = "#0A1628"):
    """Show a statistics card."""
    return f"""
    <div style="background:white;padding:15px;border-radius:10px;border:1px solid #e0e0e0;text-align:center;box-shadow:0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-size:1.5em;margin-bottom:5px;">{icon}</div>
        <div style="font-size:1.8em;font-weight:700;color:{color};">{value}</div>
        <div style="color:#666;font-size:0.85em;margin-top:4px;">{label}</div>
    </div>
    """


# ── PDF Export ───────────────────────────────────────────────────────────────

def generate_pdf(html_content: str, filename: str, output_dir: str = None) -> Path:
    """Generate PDF from HTML content using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors

    # Register Tahoma for Arabic — bundled in assets/fonts for .exe portability
    _register_pdf_fonts()

    if output_dir is None:
        output_dir = Path(__file__).parent / "generated_output"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pdf_path = output_dir / filename

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    ar_style = ParagraphStyle('Arabic', parent=styles['Normal'],
                               fontName='Tahoma', fontSize=11, leading=18,
                               alignment=1)  # RTL
    fr_style = ParagraphStyle('French', parent=styles['Normal'],
                               fontName='Helvetica', fontSize=11, leading=16,
                               alignment=0)  # LTR
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontName='Helvetica-Bold', fontSize=16,
                                  alignment=1, spaceAfter=20)


    story = []
    story.append(Paragraph("Digital Services Center", title_style))
    story.append(Spacer(1, 10))

    for line in html_content.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith('#'):
            text = line.lstrip('#').strip()
            story.append(Paragraph(text, title_style))
        elif any('\u0600' <= c <= '\u06FF' for c in line):
            story.append(Paragraph(line, ar_style))
        else:
            story.append(Paragraph(line, fr_style))

    doc.build(story)
    return pdf_path


def _register_pdf_fonts():
    """Register Tahoma (Arabic) — bundled copy first, then system fallbacks."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    if 'Tahoma' in pdfmetrics.getRegisteredFontNames():
        return
    bundled = Path(__file__).parent / "assets" / "fonts" / "Tahoma.ttf"
    bundled_b = Path(__file__).parent / "assets" / "fonts" / "Tahoma-Bold.ttf"
    # Try bundled first (works inside PyInstaller exe via _MEIPASS)
    try:
        import sys as _sys
        import pathlib as _pl
        meipass = getattr(_sys, '_MEIPASS', None)
        if meipass:
            mpass_fonts = _pl.Path(meipass) / "assets" / "fonts"
            if (mpass_fonts / "Tahoma.ttf").exists():
                bundled = mpass_fonts / "Tahoma.ttf"
                bundled_b = mpass_fonts / "Tahoma-Bold.ttf"
    except Exception:
        pass
    for name, path, fallback in [
        ('Tahoma', bundled, r'C:/Windows/Fonts/tahoma.ttf'),
        ('Tahoma-Bold', bundled_b, r'C:/Windows/Fonts/tahomabd.ttf'),
    ]:
        try:
            if Path(path).exists():
                pdfmetrics.registerFont(TTFont(name, str(path)))
            elif Path(fallback).exists():
                pdfmetrics.registerFont(TTFont(name, fallback))
        except Exception:
            pass
    # Fallback aliases so Helvetica requests don't crash if Tahoma missing
    try:
        if 'Tahoma' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Tahoma', 'Helvetica'))
        if 'Tahoma-Bold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Tahoma-Bold', 'Helvetica-Bold'))
    except Exception:
        pass

def export_page_to_pdf(content: str, page_name: str, app_instance=None):
    """Export current page content to PDF with download button."""
    filename = f"{page_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = generate_pdf(content, filename)

    if app_instance:
        app_instance.html(f"""
        <div style="background:#e8f5e9;padding:10px;border-radius:8px;margin:10px 0;">
            <strong>PDF exported:</strong> {filename}<br>
            <a href="generated_output/{filename}" download style="color:#2196F3;font-weight:bold;">
                ⬇ Download PDF
            </a>
        </div>
        """)

    return pdf_path


# ── SQLite Database ──────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "dsc_data.db"


def get_db():
    """Get SQLite database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dossiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            project_name TEXT NOT NULL,
            beneficiary_name TEXT,
            wilaya TEXT,
            activity_type TEXT,
            total_cost INTEGER,
            monthly_revenue INTEGER,
            monthly_profit INTEGER,
            status TEXT DEFAULT 'draft',
            data_json TEXT,
            content TEXT,
            pdf_path TEXT
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            name_ar TEXT,
            phone TEXT,
            email TEXT,
            wilaya TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            client_id INTEGER,
            amount INTEGER,
            description TEXT,
            status TEXT DEFAULT 'unpaid',
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_dossier(project_name: str, beneficiary_name: str = "", wilaya: str = "",
                 activity_type: str = "", total_cost: int = 0, monthly_revenue: int = 0,
                 monthly_profit: int = 0, data_json: str = "", content: str = "",
                 status: str = "draft") -> int:
    """Save a dossier to database, return dossier ID."""
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO dossiers (project_name, beneficiary_name, wilaya, activity_type,
                            total_cost, monthly_revenue, monthly_profit, data_json,
                            content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_name, beneficiary_name, wilaya, activity_type,
          total_cost, monthly_revenue, monthly_profit, data_json, content, status))
    dossier_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dossier_id


def get_dossiers(limit: int = 50, status: str = None) -> list:
    """Get list of dossiers."""
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM dossiers WHERE status=? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM dossiers ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dossier(dossier_id: int) -> Optional[dict]:
    """Get a single dossier by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM dossiers WHERE id=?", (dossier_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_dossier_status(dossier_id: int, status: str):
    """Update dossier status (draft, final, sent, paid)."""
    conn = get_db()
    conn.execute("UPDATE dossiers SET status=? WHERE id=?", (status, dossier_id))
    conn.commit()
    conn.close()


def delete_dossier(dossier_id: int):
    """Delete a dossier."""
    conn = get_db()
    conn.execute("DELETE FROM dossiers WHERE id=?", (dossier_id,))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get dashboard statistics."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM dossiers").fetchone()['c']
    final = conn.execute("SELECT COUNT(*) as c FROM dossiers WHERE status='final'").fetchone()['c']
    total_revenue = conn.execute("SELECT COALESCE(SUM(total_cost),0) as s FROM dossiers").fetchone()['s']
    total_profit = conn.execute("SELECT COALESCE(SUM(monthly_profit),0) as s FROM dossiers").fetchone()['s']
    conn.close()
    return {
        "total_dossiers": total,
        "final_dossiers": final,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
    }


# Initialize DB on import
init_db()
