from playwright.sync_api import sync_playwright
import time
import json

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501', timeout=60000)
        
        # Make a formula f1
        page.fill('input[aria-label="Type your command:"]', 'intro f1 x=y')
        page.locator('button:has-text("Run Command")').click()
        time.sleep(1)
        
        # Click the symbol 'x' in f1
        symbol = page.locator('.interactive-symbol', has_text='x').first
        symbol.scroll_into_view_if_needed()
        symbol.click()
        time.sleep(1)
        
        # Click 'st'
        page.locator('.itp-popover button:has-text("st")').click()
        time.sleep(1)
        
        # Type 't2' in the input
        page.fill('.itp-popover-input', 't2')
        time.sleep(1)
        
        # Click 'Run'
        page.locator('.itp-popover button:has-text("Run")').click()
        time.sleep(2)
        
        # Check console output
        history = page.locator('.stMarkdown', has_text='Error: No target specified').all_inner_texts()
        print(f"Error shown: {len(history) > 0}")
        
        all_text = page.locator('.stMarkdown').all_inner_texts()
        print(f"All markdown: {all_text}")
        
        browser.close()

if __name__ == '__main__':
    test_app()
