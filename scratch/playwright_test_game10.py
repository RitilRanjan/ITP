import asyncio
from playwright.async_api import async_playwright, expect

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
            
            # Step 1: cv x
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]')
            input_el = frame.locator('input').first
            await input_el.click()
            await input_el.type("cv x", delay=100)
            await page.wait_for_timeout(500)
            await page.locator('button:has-text("Run Command")').click()
            
            # Wait for command to appear in history (Note the space!)
            await expect(page.locator('strong:has-text("> cv x")')).to_be_visible(timeout=10000)
            await page.wait_for_timeout(1000)
            
            # Step 2: cf goal x=x
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]')
            input_el = frame.locator('input').first
            await input_el.click()
            await input_el.type("cf goal x=x", delay=100)
            await page.wait_for_timeout(500)
            await page.locator('button:has-text("Run Command")').click()
            
            # Wait for command to appear in history
            await expect(page.locator('strong:has-text("> cf goal x=x")')).to_be_visible(timeout=10000)
            await page.wait_for_timeout(1000)
            
            # Step 3: Click goal and apply E1
            await page.locator('.interactive-name[data-target="goal"]').click()
            await page.wait_for_timeout(1000)
            
            await page.locator('.itp-popover button:has-text("apply")').click(force=True)
            await page.wait_for_timeout(1000)
            
            await page.locator('.itp-popover-input').fill("E1")
            await page.locator('.itp-popover button:has-text("Run")').click(force=True)
            
            # Wait for game to complete
            await expect(page.locator('text="LEVEL COMPLETE!"')).to_be_visible(timeout=10000)
            print("Game completed successfully and green tick banner appeared!")
            
            # Check if Games tab shows green tick
            await page.locator('button[data-baseweb="tab"]:has-text("🎮 Games")').click()
            await page.wait_for_timeout(1000)
            await expect(page.locator('text="✅ Basics of itp"')).to_be_visible(timeout=10000)
            print("Green tick appears on game tab!")
            
        except Exception as e:
            print("Error:", e)
            await page.screenshot(path="scratch/game_error.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
