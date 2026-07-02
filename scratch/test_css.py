from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    time.sleep(3)
    container_css = page.evaluate("""() => {
        let el = document.querySelector('.stMainBlockContainer') || document.body;
        return window.getComputedStyle(el).overflow;
    }""")
    print("Container overflow:", container_css)
    browser.close()
