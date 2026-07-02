from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    time.sleep(3)
    # Find interactive symbol
    elem = page.locator('.interactive-symbol').first
    if elem:
        elem.click()
        time.sleep(1)
        # Check if popover exists
        popover = page.locator('.itp-popover')
        print(f"Popover count: {popover.count()}")
        if popover.count() > 0:
            print("Popover style:", popover.evaluate("el => el.getAttribute('style')"))
            print("Popover bounding box:", popover.bounding_box())
            print("Popover parent class:", popover.evaluate("el => el.parentNode.className"))
    browser.close()
