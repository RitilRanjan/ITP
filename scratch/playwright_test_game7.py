import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(2000)
        
        # Click the Games tab
        await page.locator('button[data-baseweb="tab"]:has-text("🎮 Games")').click()
        await page.wait_for_timeout(1000)
        
        try:
            await page.locator('button:has-text("Play")').nth(0).click()
            await page.wait_for_timeout(2000)
            
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]')
            input_el = frame.locator('input').first
            
            await input_el.click()
            await page.keyboard.type("cv x", delay=100)
            await page.wait_for_timeout(1000)
            
            # Screenshot before pressing enter to see if text is there
            await page.screenshot(path="scratch/before_run.png")
            
            await page.locator('button:has-text("Run Command")').click()
            await page.wait_for_timeout(2000)
            
            # Screenshot after run
            await page.screenshot(path="scratch/after_run.png")
            
        except Exception as e:
            print("Error:", e)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
