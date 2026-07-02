from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    time.sleep(3)
    
    # Try creating formula
    print("Filling formula")
    page.fill('input[aria-label="Input..."]', 'f1 = x \u2208 y')
    page.keyboard.press('Enter')
    time.sleep(2)
    
    # click the interactive symbol
    elem = page.locator('.interactive-symbol').first
    if elem:
        print("Clicking element")
        elem.click()
        time.sleep(1)
        
        # Output popover HTML
        popover = page.locator('.itp-popover')
        print(f"Popover count: {popover.count()}")
        if popover.count() > 0:
            print("Popover style:", popover.evaluate("el => el.getAttribute('style')"))
            
            # Now click 'st'
            btn = page.locator('.itp-popover button:has-text("st")').first
            if btn:
                print("Clicking st button inside popover")
                btn.click()
                time.sleep(1)
                print("Args popover style:", popover.evaluate("el => el.getAttribute('style')"))
                
                # Take screenshot to verify it changed to args
                page.screenshot(path='scratch/screenshot6.png')
            else:
                print("No 'st' button found")
    else:
        print("Elem not found")
    browser.close()
