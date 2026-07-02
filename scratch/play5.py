from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    time.sleep(3)
    
    # Dump all inputs
    inputs = page.locator('input').all()
    for i, inp in enumerate(inputs):
        print(f"Input {i}: placeholder={inp.get_attribute('placeholder')}, aria-label={inp.get_attribute('aria-label')}")
    
    browser.close()
