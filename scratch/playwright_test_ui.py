from playwright.sync_api import sync_playwright
import time
import re

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501')
        time.sleep(2)
        
        # We know filling 'Program Name' fails sometimes. Let's find the text_input by label properly.
        # Streamlit renders labels above inputs. Let's find the label with text 'Program Name', 
        # then find its related input.
        print("Loading program 'ritil1'...")
        try:
            page.locator('input[aria-label="Program Name"]').fill('ritil1')
            time.sleep(1)
            page.locator('button:has-text("Load")').click()
            time.sleep(3)
        except Exception as e:
            print("Failed to load program:", e)
            browser.close()
            return
            
        print("Finding 'x'...")
        symbols = page.locator('span[data-symbol="x"]')
        if symbols.count() > 0:
            symbols.first.click()
            time.sleep(1)
            
            print("Clicking 'st'...")
            page.locator('button:has-text("st")').click()
            time.sleep(1)
            
            print("Typing 't2'...")
            page.locator('.itp-popover-input').fill('t2')
            time.sleep(1)
            
            print("Clicking Run...")
            page.locator('button:has-text("Run")').click()
            time.sleep(3)
        else:
            print("Could not find 'x' symbol.")
            
        print("CHECKING CONSOLE OUTPUT...")
        # Get all markdown elements
        texts = page.locator('.stMarkdown').all_inner_texts()
        for t in texts:
            if "ITP" in t or "Error" in t or "st " in t:
                print("---")
                print(t)
        
        page.screenshot(path="scratch/final_ui.png")
        print("Screenshot saved to scratch/final_ui.png")
        
        browser.close()

if __name__ == '__main__':
    test_app()
