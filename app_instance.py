"""
Shared app instance — Violit-based.
All pages import from here for `app`, helpers, and shared utilities.
"""
import sys
from pathlib import Path

import violit as vl

sys.path.insert(0, str(Path(__file__).parent))

from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA

app = vl.App(title="Digital Services Center", theme="ocean")


def _fmt(n):
    """Format number with thousand separators."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _sidebar():
    """Shared sidebar navigation."""
    with app.sidebar:
        app.html("""
        <div style="padding:10px 0;border-bottom:1px solid #ddd;margin-bottom:10px;">
            <h3 style="margin:0;color:#0A1628;">DSC</h3>
            <p style="margin:2px 0 0;font-size:0.85em;color:#666;">مركز الخدمات الرقمية</p>
        </div>
        """)
        app.markdown("### Navigation")


def _provider_select():
    """Shared provider selectbox."""
    return app.selectbox("AI Provider", options=["groq", "openrouter", "aihubmix"], index=0)


def _wilaya_select():
    """Shared wilaya selectbox."""
    return app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)


def _save_output(doc_type: str, name: str, content: str, filename_suffix: str = ""):
    """Save generated content to output directory."""
    output_dir = Path(__file__).parent / "generated_output"
    output_dir.mkdir(exist_ok=True)
    safe_name = name.replace(" ", "_").replace("/", "_")
    ext = "md"
    if filename_suffix:
        filename = f"{doc_type}_{safe_name}_{filename_suffix}"
    else:
        filename = f"{doc_type}_{safe_name}.{ext}"
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    app.toast(f"Saved: {filename}", variant="success")
    return filepath
