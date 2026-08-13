"""E2E test: open all expanders via JS, fill CV Generator, generate."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

SCREENSHOTS = "C:/Users/Admin/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8000", wait_until="networkidle")
    page.wait_for_timeout(1500)

    # === CV Generator ===
    page.evaluate("window.sendAction('nav_menu_0', 'page_cv-generator')")
    page.wait_for_timeout(2000)

    # Open ALL expanders via JS
    page.evaluate("""() => {
        document.querySelectorAll('wa-details').forEach(e => {
            e.setAttribute('open', '');
            e.open = true;
        });
    }""")
    page.wait_for_timeout(1000)

    # Fill Personal Info
    page.locator('wa-input[label="Full Name"]').locator('input').fill("MAHI Kamel Abdelghani", force=True)
    page.locator('wa-input[label="Title (EN)"]').locator('input').fill("English Teacher & EdTech Developer", force=True)
    page.locator('wa-input[label="Title (AR)"]').locator('input').fill("مدرس اللغة الإنجليزية ومطور التعليم", force=True)
    page.locator('wa-input[label="Email"]').locator('input').fill("kamelmahi71@gmail.com", force=True)
    page.locator('wa-input[label="Phone"]').locator('input').fill("+213 555081718", force=True)
    page.locator('wa-input[label="Address"]').locator('input').fill("El Bayadh, Algerie", force=True)
    print("1. Personal Info filled")

    # Fill Objective
    page.locator('wa-textarea[label="Objective (EN)"]').locator('textarea').fill("English teacher with expertise in AI-powered educational systems", force=True)
    print("2. Objective filled")

    # Fill Skills
    page.locator('wa-textarea[label="Skills (comma-separated)"]').locator('textarea').fill("Python, JavaScript, VBA, Claude API, Prompt Engineering, English Teaching", force=True)
    print("3. Skills filled")

    # Fill Experience
    page.locator('wa-input[label="Position 1"]').locator('input').fill("English Teacher", force=True)
    page.locator('wa-input[label="Company 1"]').locator('input').fill("Various Schools", force=True)
    page.locator('wa-input[label="Period 1"]').locator('input').fill("2020-2025", force=True)
    page.locator('wa-textarea[label="Responsibilities 1"]').locator('textarea').fill("Teaching English, developing AI-powered lesson plans", force=True)
    print("4. Experience filled")

    # Re-open all expanders (they may have collapsed)
    page.evaluate("""() => {
        document.querySelectorAll('wa-details').forEach(e => {
            e.setAttribute('open', '');
            e.open = true;
        });
    }""")
    page.wait_for_timeout(500)

    # Fill Education
    page.locator('wa-input[label="Degree 1"]').locator('input').fill("BA in English Language", force=True)
    page.locator('wa-input[label="Institution 1"]').locator('input').fill("Dr. Moulay Tahar University, Saida", force=True)
    page.locator('wa-input[label="Year 1"]').locator('input').fill("2020", force=True)
    print("5. Education filled")

    # Fill Languages & Certs
    page.locator('wa-textarea[label="Languages"]').locator('textarea').fill("Arabic (Native), English (C1), French (B1)", force=True)
    page.locator('wa-textarea[label="Certifications"]').locator('textarea').fill("CCA-F (In Progress), BTS Stock Management", force=True)
    print("6. Languages & Certs filled")

    page.wait_for_timeout(500)
    page.screenshot(path=f"{SCREENSHOTS}/e2e_cv_01_filled.png")
    print("All CV fields filled!")

    # Click Generate
    page.locator('wa-button:has-text("Generate")').click()
    print("Clicked Generate CV")

    page.wait_for_timeout(6000)
    page.evaluate('window.scrollTo(0, 0)')
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS}/e2e_cv_02_result.png")

    # Check result
    body_text = page.inner_text('body')
    for line in body_text.split('\n'):
        line = line.strip()
        if line and len(line) < 200 and any(k in line.lower() for k in ['error', 'success', 'generated', 'pdf', 'failed', 'saved', 'exception', 'cv']):
            print(f"CV RESULT: {line}")

    # === AAPI Scorer ===
    page.evaluate("window.sendAction('nav_menu_0', 'page_aapi-scorer')")
    page.wait_for_timeout(2000)

    # Open all expanders
    page.evaluate("""() => {
        document.querySelectorAll('wa-details').forEach(e => {
            e.setAttribute('open', '');
            e.open = true;
        });
    }""")
    page.wait_for_timeout(1000)

    # List all inputs
    aapi_inputs = page.locator('wa-input')
    count = aapi_inputs.count()
    print(f"\nAAPI: Found {count} wa-inputs")
    for i in range(count):
        label = aapi_inputs.nth(i).get_attribute('label') or ""
        print(f"  Input {i}: '{label}'")

    # Fill by label (try both with and without accents)
    fill_map = {
        "Nature": "15",
        "Montant de l'investissement": "10",
        "Emploi": "8",
        "Montant des apports": "5",
        "Contribution": "20",
    }
    for i in range(count):
        label = aapi_inputs.nth(i).get_attribute('label') or ""
        for key, val in fill_map.items():
            if key.lower() in label.lower():
                aapi_inputs.nth(i).locator('input').fill(val, force=True)
                print(f"  Filled '{label}' = {val}")
                break

    # Check checkboxes
    checkboxes = page.locator('wa-checkbox')
    cb_count = checkboxes.count()
    print(f"AAPI: Found {cb_count} checkboxes")
    for i in range(cb_count):
        label = checkboxes.nth(i).get_attribute('label') or ""
        print(f"  Checkbox {i}: '{label}'")

    page.wait_for_timeout(500)
    page.screenshot(path=f"{SCREENSHOTS}/e2e_aapi_01_filled.png")

    # Click Score
    score_btns = page.locator('wa-button')
    for i in range(score_btns.count()):
        txt = score_btns.nth(i).inner_text().strip()
        print(f"  Button {i}: '{txt}'")
        if 'score' in txt.lower() or 'aapi' in txt.lower() or 'evaluer' in txt.lower():
            score_btns.nth(i).click()
            print(f"  Clicked: {txt}")
            break

    page.wait_for_timeout(4000)
    page.evaluate('window.scrollTo(0, 0)')
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS}/e2e_aapi_02_result.png")

    body_text = page.inner_text('body')
    for line in body_text.split('\n'):
        line = line.strip()
        if line and len(line) < 200 and any(k in line.lower() for k in ['error', 'success', 'score', 'total', 'result', 'failed', 'saved', 'exception', 'points', '/100']):
            print(f"AAPI RESULT: {line}")

    browser.close()
    print("\nAll E2E tests complete!")
