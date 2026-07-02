import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to Streamlit app...")
        await page.goto("http://localhost:8501")
        
        print("Waiting for Streamlit app to load...")
        # Wait for the chat input container to be visible
        await page.wait_for_selector('input[aria-label="Enter command here"]', timeout=30000)
        
        print("Initializing definitions...")
        input_element = page.locator('input[aria-label="Enter command here"]')
        
        # Test fold on quantifier
        await input_element.fill('def_f f1 ∀x (x = x)')
        await input_element.press('Enter')
        await page.wait_for_timeout(1000)
        
        # Start a mission to make them interactive
        await input_element.fill('mission m1 f1')
        await input_element.press('Enter')
        await page.wait_for_timeout(1000)
        
        print("Waiting for interactive symbol...")
        # Now there should be an interactive-symbol
        symbols = page.locator('.interactive-symbol')
        count = await symbols.count()
        print(f"Found {count} interactive symbols.")
        if count == 0:
            print("ERROR: No interactive symbols found!")
            await page.screenshot(path="scratch/error_no_symbols.png")
            return
            
        print("Clicking first symbol (∀)...")
        await symbols.first.click()
        await page.wait_for_timeout(1000)
        
        print("Checking popover commands...")
        buttons = page.locator('.itp-popover button')
        btn_count = await buttons.count()
        cmds = []
        for i in range(btn_count):
            cmds.append(await buttons.nth(i).inner_text())
            
        print(f"Commands for ∀: {cmds}")
        if 'fold' in cmds:
            print("SUCCESS: 'fold' command is present for ∀!")
        else:
            print("ERROR: 'fold' command missing!")
            await page.screenshot(path="scratch/error_no_fold.png")
            
        # Now click the name of the formula
        print("Clicking interactive name (m1)...")
        name = page.locator('.interactive-name').first
        await name.click()
        await page.wait_for_timeout(1000)
        
        buttons = page.locator('.itp-popover button')
        btn_count = await buttons.count()
        cmds = []
        for i in range(btn_count):
            cmds.append(await buttons.nth(i).inner_text())
            
        print(f"Commands for name: {cmds}")
        if 'fold all' in cmds:
            print("SUCCESS: 'fold all' command is present for name!")
        else:
            print("ERROR: 'fold all' command missing!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
