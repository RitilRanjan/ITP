from playwright.sync_api import sync_playwright
import time

def test_scroll():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        time.sleep(5)
        
        page.screenshot(path="scratch/screenshot.png")
        print("Screenshot saved.")
        browser.close()

if __name__ == "__main__":
    test_scroll()
