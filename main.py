"""
Digital Services Center — Violit App
Main entry point — navigation via violit.Page, all page logic in pages/.
"""
import violit as vl

from app_instance import app
from pages import (
    home_page, feasibility_page, business_plan_page, market_research_page,
    financial_projections_page, marketing_plan_page, social_media_page,
    pricing_page, invoice_page, g12_page, g50_page, tax_guides_page,
    cv_generator_page, cover_letter_page, government_page, calculators_page,
    aapi_page, batch_page, nesda_calc_page, nesda_catalog_page,
    eligibility_page, linkedin_page, social_content_page, social_analytics_page,
    social_scheduling_page, social_engagement_page, complete_dossier_page, bmc_page,
    orchestrated_dossier_page, dossier_page,
)

app.navigation([
    vl.Page(home_page, title="Home", icon="house"),
    vl.Page(complete_dossier_page, title="Complete Dossier", icon="package"),
    vl.Page(orchestrated_dossier_page, title="One-Click Dossier", icon="zap"),
    vl.Page(dossier_page, title="NESDA 9-Part", icon="file-text"),
    vl.Page(feasibility_page, title="Feasibility", icon="file-text"),
    vl.Page(business_plan_page, title="Business Plan", icon="briefcase"),
    vl.Page(market_research_page, title="Market Research", icon="bar-chart"),
    vl.Page(financial_projections_page, title="Financials", icon="trending-up"),
    vl.Page(bmc_page, title="BMC Canvas", icon="layout"),
    vl.Page(nesda_calc_page, title="NESDA Calc", icon="calculator"),
    vl.Page(nesda_catalog_page, title="NESDA Catalog", icon="search"),
    vl.Page(eligibility_page, title="Eligibility", icon="check-circle"),
    vl.Page(pricing_page, title="Pricing", icon="dollar-sign"),
    vl.Page(marketing_plan_page, title="Marketing Plan", icon="megaphone"),
    vl.Page(social_media_page, title="Social Media", icon="share-2"),
    vl.Page(g12_page, title="G12 IFU", icon="file-text"),
    vl.Page(g50_page, title="G50 Monthly", icon="file"),
    vl.Page(tax_guides_page, title="Tax Guides", icon="book"),
    vl.Page(invoice_page, title="Invoice/Quote", icon="file"),
    vl.Page(cv_generator_page, title="CV Generator", icon="user"),
    vl.Page(cover_letter_page, title="Cover Letter", icon="mail"),
    vl.Page(government_page, title="Gov Paperwork", icon="building"),
    vl.Page(calculators_page, title="Calculators", icon="calculator"),
    vl.Page(aapi_page, title="AAPI Scorer", icon="award"),
    vl.Page(linkedin_page, title="LinkedIn", icon="linkedin"),
    vl.Page(social_content_page, title="Social Content", icon="share-2"),
    vl.Page(social_analytics_page, title="Social Analytics", icon="bar-chart"),
    vl.Page(social_scheduling_page, title="Social Scheduling", icon="calendar"),
    vl.Page(social_engagement_page, title="Social Engagement", icon="message-circle"),
    vl.Page(batch_page, title="Batch Process", icon="layers"),
])

if __name__ == "__main__":
    app.run()
