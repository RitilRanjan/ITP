from playwright.sync_api import sync_playwright

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_timeout(3000)
        page.screenshot(path="screenshot.png", full_page=True)
        browser.close()
        print("Screenshot saved to screenshot.png")

if __name__ == "__main__":
    capture()
