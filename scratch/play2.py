from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    time.sleep(3)
    # create formula first!
    page.fill('input[aria-label="Input..."]', 'f1 = x \u2208 y')
    page.keyboard.press('Enter')
    time.sleep(2)
    
    # click the interactive symbol
    elem = page.locator('.interactive-symbol').first
    if elem:
        elem.click()
        time.sleep(1)
        page.screenshot(path='scratch/screenshot.png')
        print("Took screenshot")
    else:
        print("Elem not found")
    browser.close()
