from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8502')
        time.sleep(3)
        page.screenshot(path="scratch/expander_test.png", full_page=True)
        browser.close()

test_app()
