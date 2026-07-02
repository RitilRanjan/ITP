import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(2000)
        
        await page.locator('button[data-baseweb="tab"]:has-text("🎮 Games")').click()
        await page.wait_for_timeout(1000)
        
        try:
            await page.locator('button:has-text("Play")').nth(0).click()
            await page.wait_for_timeout(2000)
            
            # Use Enter key to trigger the JS listener
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]')
            
            await frame.locator('input').first.click()
            await page.keyboard.type("cv x", delay=100)
            await page.wait_for_timeout(500)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000) # Wait for rerun
            
            # After rerun, iframe might be recreated
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]')
            await frame.locator('input').first.click()
            await page.keyboard.type("cf goal x=x", delay=100)
            await page.wait_for_timeout(500)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000)
            
            await page.locator('.interactive-name[data-target="goal"]').click()
            await page.wait_for_timeout(1000)
            
            await page.locator('.itp-popover button:has-text("apply")').click(force=True)
            await page.wait_for_timeout(1000)
            
            await page.locator('.itp-popover-input').fill("E1")
            await page.locator('.itp-popover button:has-text("Run")').click(force=True)
            await page.wait_for_timeout(2000)
            
            if await page.locator('text="LEVEL COMPLETE!"').is_visible():
                print("Game completed successfully and green tick banner appeared!")
                await page.screenshot(path="scratch/game_complete.png")
            else:
                print("Failed to complete game.")
                await page.screenshot(path="scratch/game_fail.png")
                
        except Exception as e:
            print("Error:", e)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
