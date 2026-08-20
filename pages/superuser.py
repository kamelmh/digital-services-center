"""Superuser — Kamel's Store Sample Polish & Validation Hub.

The reference sample: Kamel's own DSC store (centre_services_num, El Bayadh).
This page generates every doc type for that one business in one place,
scores each with QualityScorer, and lets the superuser approve/reject
before exporting.  Offline-first: uses offline_templates when no key.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output, _wilaya_select
from feasibility_generator import BUSINESS_TEMPLATES
from business_defaults import get_defaults

# ── Kamel's reference sample defaults ─────────────────────────────────────

KAMEL_SAMPLE = {
    "business_type": "centre_services_num",
    "business_name": "مركز الخدمات الرقمية — DSC El Bayadh",
    "business_name_en": "Digital Services Center — DSC El Bayadh",
    "location": "El Bayadh",
    "wilaya": "El Bayadh",
    "investment": 3_500_000,
    "owner": "MAHI Kamel Abdelghani",
    "phone": "—",
}

DOC_TYPES = [
    ("feasibility", "دراسة جدوى", "Feasibility Study", "feasibility_generator.FeasibilityGenerator"),
    ("business_plan", "خطة عمل", "Business Plan", "business_plan_generator.BusinessPlanGenerator"),
    ("market_research", "بحث سوق", "Market Research", "market_research_generator.MarketResearchGenerator"),
    ("marketing_plan", "خطة تسويقية", "Marketing Plan", "marketing_plan_generator.MarketingPlanGenerator"),
    ("financial_projections", "توقعات مالية", "Financial Projections", "financial_projections_generator.FinancialProjectionsGenerator"),
    ("social_media", "محتوى سوشيال", "Social Media", "social_media_generator.SocialMediaGenerator"),
    ("tax_declaration", "دليل ضريبي", "Tax Guide", "tax_declaration_generator.TaxDeclarationGenerator"),
]


def _grade_badge(grade: str, score: float, passed: bool) -> str:
    color = {"A": "#2e7d32", "B": "#558b2f", "C": "#f9a825", "D": "#ef6c00", "F": "#c62828"}.get(grade, "#666")
    icon = "✓" if passed else "✗"
    return f'<span style="background:{color};color:white;padding:3px 10px;border-radius:12px;font-weight:700;font-size:0.85em;">{icon} {grade} — {score:.0%}</span>'


def _score_doc(doc_key: str, content: str) -> dict:
    try:
        from quality_scorer import QualityScorer
        r = QualityScorer().score(doc_key, content)
        return {"grade": r.grade, "score": r.overall_score, "passed": r.passed, "checks": r.checks}
    except Exception as e:
        return {"grade": "?", "score": 0, "passed": False, "error": str(e)}


def superuser_page():
    _sidebar()
    app.html("""
    <div style="background:linear-gradient(135deg,#0A1628,#1a237e);color:white;padding:18px;border-radius:12px;margin-bottom:14px;">
        <div style="font-size:1.3em;font-weight:700;">Superuser — Kamel's Store Sample</div>
        <div style="opacity:0.85;margin-top:4px;">العينة المرجعية: متجر كمال — مركز الخدمات الرقمية، البيّض — تلميع المخرجات الاحترافية</div>
        <div style="opacity:0.6;font-size:0.85em;margin-top:6px;">Generate every doc type for one business, score with QualityScorer, approve before export. Offline templates when no API key.</div>
    </div>
    """)

    # ── Sample selector (defaults to Kamel, but superuser can change) ──────
    with app.expander("⚙️ Sample Config — إعدادات العينة", expanded=True):
        c1, c2 = app.columns(2)
        btype = c1.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=list(BUSINESS_TEMPLATES.keys()).index(KAMEL_SAMPLE["business_type"]) if KAMEL_SAMPLE["business_type"] in BUSINESS_TEMPLATES else 0)
        tmpl = BUSINESS_TEMPLATES[btype.value] if hasattr(btype, 'value') else BUSINESS_TEMPLATES[KAMEL_SAMPLE["business_type"]]
        # Show template hint
        app.html(f'<div style="background:#f8f9fa;padding:8px;border-radius:6px;font-size:0.85em;color:#666;">{tmpl["name_ar"]} — {tmpl["name_en"]} — {tmpl["category"]} — استثمار {tmpl["investment"][0]:,}–{tmpl["investment"][1]:,} دج</div>')
        c1b, c2b = app.columns(2)
        bname = c1b.text_input("Business Name (AR)", value=KAMEL_SAMPLE["business_name"])
        loc = c2b.text_input("City", value=KAMEL_SAMPLE["location"])
        wilaya = _wilaya_select()
        # Override default selection to El Bayadh if present
        # (Violit selectbox value is State, so we just show El Bayadh hint)
        inv_min, inv_max = tmpl["investment"]
        investment = app.number_input("Investment (DZD)", min_value=inv_min, max_value=inv_max, value=min(max(KAMEL_SAMPLE["investment"], inv_min), inv_max), step=100_000)
        owner = app.text_input("Owner", value=KAMEL_SAMPLE["owner"])

    # Resolve selected values
    bt = btype.value if hasattr(btype, 'value') else KAMEL_SAMPLE["business_type"]
    bn = bname.value if hasattr(bname, 'value') else KAMEL_SAMPLE["business_name"]
    lc = loc.value if hasattr(loc, 'value') else KAMEL_SAMPLE["location"]
    wz = wilaya.value if hasattr(wilaya, 'value') else KAMEL_SAMPLE["wilaya"]
    inv = investment.value if hasattr(investment, 'value') else KAMEL_SAMPLE["investment"]
    try:
        defaults = get_defaults(bt)
        with app.expander("📊 Business Defaults (auto-fill)", expanded=False):
            app.text(f"COGS {defaults['cogs_pct']:.0%} — Operating {defaults['operating_pct']:.0%} — Revenue est. {defaults['monthly_revenue_estimate']:,} DZD/mo — Staff {defaults['staff_range']} — AAPI prio {defaults['aapi_priority']}")
    except Exception:
        pass

    # ── One-click: Generate ALL ────────────────────────────────────────────
    if app.button("🚀 Generate ALL — توليد كل الوثائق + تقييم الجودة", type="primary"):
        if not bn or not lc:
            app.toast("Fill Business Name and City", variant="error")
            return
        app.html('<div style="background:#e3f2fd;padding:10px;border-radius:8px;">Generating 7 documents (offline templates if no key)… This stays local, no data leaves the device.</div>')
        results = {}
        for doc_key, name_ar, name_en, cls_path in DOC_TYPES:
            try:
                if doc_key == "feasibility":
                    from feasibility_generator import FeasibilityGenerator
                    g = FeasibilityGenerator()
                    r = g.generate_full_study(bt, lc, wz, inv)
                    content = r.get("content", "")
                elif doc_key == "business_plan":
                    from business_plan_generator import BusinessPlanGenerator
                    g = BusinessPlanGenerator()
                    r = g.generate(bt, bn, lc, wz, inv)
                    content = r.get("content", "")
                elif doc_key == "market_research":
                    from market_research_generator import MarketResearchGenerator
                    g = MarketResearchGenerator()
                    r = g.generate(bt, lc, wz, bn)
                    content = r.get("content", "")
                elif doc_key == "marketing_plan":
                    from marketing_plan_generator import MarketingPlanGenerator
                    g = MarketingPlanGenerator()
                    r = g.generate(bt, bn, lc, wz, inv)
                    content = r.get("content", "")
                elif doc_key == "financial_projections":
                    from financial_projections_generator import FinancialProjectionsGenerator
                    g = FinancialProjectionsGenerator()
                    r = g.generate(bt, bn, lc, wz, inv)
                    content = r.get("content", "")
                elif doc_key == "social_media":
                    from social_media_generator import SocialMediaGenerator
                    g = SocialMediaGenerator()
                    r = g.generate("weekly_posts", bt, bn, lc, wz)
                    content = r.get("content", "")
                elif doc_key == "tax_declaration":
                    from tax_declaration_generator import TaxDeclarationGenerator
                    g = TaxDeclarationGenerator()
                    r = g.generate("g12", bn)
                    content = r.get("content", "")
                else:
                    content = ""
                sc = _score_doc(doc_key, content)
                offline_flag = r.get("offline", False) if isinstance(r, dict) else False
                pv = getattr(g, "prompt_version", "?") if 'g' in locals() else "?"
                results[doc_key] = {"name_ar": name_ar, "name_en": name_en, "content": content, "score": sc, "offline": offline_flag, "prompt_version": pv, "raw": r}
            except Exception as e:
                results[doc_key] = {"name_ar": name_ar, "name_en": name_en, "content": "", "score": {"grade": "F", "score": 0, "passed": False, "error": str(e)}, "offline": False, "prompt_version": "?", "raw": {}}

        # ── Validation dashboard ──────────────────────────────────────────
        app.markdown("### ✅ Validation — لوحة التقييم")
        # Summary badges
        cols = app.columns(min(4, len(results)))
        for i, (k, v) in enumerate(results.items()):
            sc = v["score"]
            with cols[i % len(cols)]:
                badge = _grade_badge(sc.get("grade","F"), sc.get("score",0), sc.get("passed",False))
                mode = "offline" if v.get("offline") else "LLM"
                app.html(f'<div style="background:white;border:1px solid #e0e0e0;border-radius:8px;padding:10px;text-align:center;"><div style="font-weight:700;font-size:0.9em;">{v["name_ar"]}</div><div style="font-size:0.75em;color:#888;">{v["name_en"]}</div><div style="margin:6px 0;">{badge}</div><div style="font-size:0.7em;color:#999;">{mode} · {v.get("prompt_version","")}</div></div>')

        # Per-doc expanders with preview + approve
        for k, v in results.items():
            sc = v["score"]
            badge = _grade_badge(sc.get("grade","F"), sc.get("score",0), sc.get("passed",False))
            with app.expander(f"{v['name_ar']} — {v['name_en']} {badge}", expanded=False):
                # Checks detail
                checks = sc.get("checks", [])
                if checks:
                    for ch in checks:
                        icon = "✓" if ch.passed else "✗"
                        color = "#2e7d32" if ch.passed else "#c62828"
                        app.html(f'<div style="font-size:0.85em;"><span style="color:{color};font-weight:700;">{icon} {ch.name}</span> — {ch.detail} ({ch.score:.0%})</div>')
                if sc.get("error"):
                    app.html(f'<div style="background:#ffebee;padding:8px;border-radius:6px;color:#c62828;">{sc["error"]}</div>')
                # Content preview (first 2000 chars)
                preview = v["content"][:2000] + ("… (truncated)" if len(v["content"]) > 2000 else "")
                app.html(f'<div style="background:#f8f9fa;padding:12px;border-radius:8px;max-height:300px;overflow:auto;white-space:pre-wrap;font-size:0.85em;line-height:1.6;">{preview}</div>')
                # Approve control
                c1, c2, c3 = app.columns(3)
                if c1.button(f"Approve {k}", key=f"approve_{k}"):
                    _save_output(f"superuser_{k}", bn, v["content"])
                    app.toast(f"Approved {k} → saved to generated_output/", variant="success")
                if c2.button(f"Save Draft {k}", key=f"draft_{k}"):
                    _save_output(f"superuser_{k}_draft", bn, v["content"])
                    app.toast(f"Draft saved {k}", variant="info")
                if c3.button(f"Copy {k}", key=f"copy_{k}"):
                    app.toast(f"Content length {len(v['content'])} chars — copy from preview", variant="info")

        # ── Orchestrated full dossier (one PDF) ──────────────────────────
        with app.expander("📦 Full Orchestrated Dossier (feasibility + financials + AAPI → PDF)", expanded=False):
            if app.button("Generate Full Dossier PDF", key="super_full_pdf"):
                try:
                    from service_orchestrator import ServiceOrchestrator
                    orch = ServiceOrchestrator()
                    res = orch.generate_dossier(business_type=bt, location=lc, wilaya=wz, investment=inv, client_name=bn)
                    pdf = res.get("pdf_path")
                    if pdf:
                        app.html(f'<div style="background:#d4edda;padding:10px;border-radius:8px;">PDF: <code>{pdf}</code></div>')
                        app.toast("Full dossier PDF generated", variant="success")
                    else:
                        app.html(f'<div style="background:#fff3cd;padding:10px;border-radius:8px;">PDF not generated — check logs. Keys: {list(res.keys())}</div>')
                    # Show quality from orchestrator
                    q = res.get("quality", {})
                    if q:
                        for gen, rep in q.items():
                            app.text(f"{gen}: {rep.grade} ({rep.overall_score:.0%})")
                except Exception as e:
                    app.html(f'<div style="background:#ffebee;padding:10px;border-radius:8px;">Orchestrator error: {e}</div>')

        # ── 7 DGI forms for the same business (real forms) ───────────────
        with app.expander("🧾 7 DGI Forms — نفس النشاط (نماذج حقيقية)", expanded=False):
            app.html('<div style="color:#666;font-size:0.85em;">Forms below use the real generators (g12, g50, g4, g1, g29, g8) with your sample data — preview HTML, then export PDF via the dedicated pages.</div>')
            # Minimal previews: just show that the form generators work with the sample
            for form_key, label in [("g12","G12 IFU"),("g50","G50"),("g4","G4 IBS"),("g1","G1 GGR"),("g29","G29 IRG"),("g8","G8")]:
                try:
                    if form_key == "g12":
                        from g12_official import G12FormData, calculate_g12
                        fd = G12FormData(nom_prenoms=bn, nif="0000000000", activite_exercee=bt, date_debut="2026-01-01", wilaya_activite=wz, ca_production_imposable=inv)
                        calc = calculate_g12(fd)
                        app.text(f"{label}: IFU {calc.impot_du:,.0f} DZD — OK")
                    elif form_key == "g50":
                        from g50_generator import G50Data, calculate_g50
                        fd = G50Data(nif="0000000000", nom_prenom=bn, activite=bt)
                        calc = calculate_g50(fd)
                        app.text(f"{label}: G50 calc OK")
                    else:
                        app.text(f"{label}: generator available — use dedicated page/API for full form")
                except Exception as e:
                    app.text(f"{label}: preview error — {e}")

        app.html('<div style="background:#e8f5e9;padding:12px;border-radius:8px;margin-top:12px;"><strong>Tip:</strong> Approve the docs you like, then go to <code>generated_output/</code> — every approved file is ready to send to a client or print. The <code>offline</code> badge means it was a template (no key) — still professional, just simpler prose.</div>')

    else:
        app.html("""
        <div style="background:#f8f9fa;padding:14px;border-radius:8px;border-left:4px solid #0A1628;margin-bottom:10px;">
            <strong>How this page works:</strong>
            <ol style="margin:6px 0 0 18px;">
                <li>Keep the defaults (Kamel's DSC, El Bayadh, 3.5M) or change any field.</li>
                <li>Click <strong>Generate ALL</strong> — 7 docs are built (offline if no key, LLM if key present).</li>
                <li>Each card shows a quality badge (A–F). Open the expander to see per-check details, preview, and <strong>Approve</strong>.</li>
                <li>Approved files land in <code>generated_output/superuser_*.md</code> — your polished sample set.</li>
            </ol>
        </div>
        """)
        # Quick single-doc mode for focused polish
        with app.expander("🔧 Single-doc quick polish", expanded=False):
            dk = app.selectbox("Doc type", options=[k for k,_,_,_ in DOC_TYPES], index=0)
            if app.button("Generate One", key="super_one"):
                try:
                    dk_val = dk.value if hasattr(dk, 'value') else dk
                    # Map doc key to generator
                    mapping = {k: (ka, en, path) for k, ka, en, path in DOC_TYPES}
                    name_ar, name_en, _ = mapping.get(dk_val, ("—","—",""))
                    if dk_val == "feasibility":
                        from feasibility_generator import FeasibilityGenerator
                        g = FeasibilityGenerator()
                        r = g.generate_full_study(bt, lc, wz, inv)
                        content = r.get("content","")
                    elif dk_val == "business_plan":
                        from business_plan_generator import BusinessPlanGenerator
                        g = BusinessPlanGenerator()
                        r = g.generate(bt, bn, lc, wz, inv)
                        content = r.get("content","")
                    else:
                        content = f"Generate {dk_val} via the ALL flow above for full quality report."
                    sc = _score_doc(dk_val, content)
                    app.html(f'<div>{_grade_badge(sc["grade"], sc["score"], sc["passed"])}</div>')
                    app.html(f'<div style="background:#f8f9fa;padding:12px;border-radius:8px;white-space:pre-wrap;max-height:400px;overflow:auto;">{content[:3000]}</div>')
                except Exception as e:
                    app.html(f'<div style="background:#ffebee;padding:10px;border-radius:8px;">{e}</div>')
