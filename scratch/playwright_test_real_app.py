from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501', timeout=60000)
        time.sleep(2)
        
        # Load ritil1 program
        page.fill('input[aria-label="Program Name"]', 'ritil1')
        time.sleep(1)
        page.locator('button:has-text("Load")').click()
        time.sleep(2)
        
        # Check chat history before
        print("BEFORE:")
        for txt in page.locator('.stMarkdown').all_inner_texts():
            if "ITP" in txt:
                print(txt)
                
        # Click the variable 'x'
        symbols = page.locator('span[data-symbol="x"]')
        if symbols.count() > 0:
            print(f"Found {symbols.count()} 'x' symbols.")
            symbols.first.click()
            time.sleep(1)
            
            # Click st
            page.locator('button:has-text("st")').click()
            time.sleep(1)
            
            # Type t2
            page.locator('.itp-popover-input').fill('t2')
            time.sleep(1)
            
            # Click Run
            page.locator('button:has-text("Run")').click()
            time.sleep(3)
        else:
            print("No 'x' symbol found.")
        
        # Check chat history after
        print("AFTER:")
        for txt in page.locator('.stMarkdown').all_inner_texts():
            if "ITP" in txt or "Error:" in txt:
                print(txt)
        
        browser.close()

if __name__ == '__main__':
    test_app()
